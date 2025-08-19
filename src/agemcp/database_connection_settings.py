
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Self

from pydantic import BaseModel, Field, PrivateAttr, field_validator
from pydantic.types import SecretStr
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine
from typing_extensions import Literal

from agemcp.data_source_name import DataSourceName


class DatabaseConnectionSettings(BaseModel):
    """A single database connection configuration with a mandatory _name_ and _dsn_."""

    # Required
    name                      : str                  = Field(...,            description="Unique name for this database connection")
    dsn                       : DataSourceName       = Field(...,            description="Data Source Name (DSN) for this database connection")

    # Optional
    echo                      : bool                 = Field(default=False,  description="Enable SQL statement logging")
    encoding                  : str                  = Field(default="utf8", description="Client encoding")
    timezone                  : str                  = Field(default="UTC",  description="IANA timezone name (e.g., 'America/New_York', ISO 8601/ISO 3166)")
    readonly                  : bool                 = Field(default=False,  description="Open connection in read-only mode")

    connection_timeout        : int | None           = Field(default=10,     description="Connection timeout in seconds")
    command_timeout           : int | None           = Field(default=None,   description="Command execution timeout in seconds, None for no timeout")

    # Connection pool settings
    pool_min_connections      : int | None           = Field(default=5,      description="Minimum number of connections in the pool")
    pool_max_connections      : int | None           = Field(default=10,     description="Maximum number of connections in the pool")
    pool_max_idle_time        : int | None           = Field(default=300,    description="Maximum idle time for connections in the pool (seconds)")
    pool_max_lifetime         : int | None           = Field(default=3600,   description="Maximum lifetime for connections in the pool (seconds)")
    pool_recycle_time         : int | None           = Field(default=1800,   description="Time after which connections are recycled (seconds)")
    pool_pre_ping             : bool                 = Field(default=True,   description="Enable pre-ping to check connection health")
    pool_max_overflow         : int | None           = Field(default=10,     description="Number of connections that can be created beyond the pool size limit")

    keepalives                : bool                 = Field(default=True,   description="Enable TCP keepalives")
    keepalives_idle           : int | None           = Field(default=60,     description="TCP keepalive idle time (seconds)")
    keepalives_interval       : int | None           = Field(default=10,     description="TCP keepalive interval (seconds)")
    keepalives_count          : int | None           = Field(default=5,      description="TCP keepalive probe count")


    _sqlalchemy_async_engine: AsyncEngine | None = PrivateAttr(default=None)
    _sqlalchemy_sync_engine: Engine | None = PrivateAttr(default=None)

    @field_validator('dsn', mode='before')
    @classmethod
    def validate_dsn(cls, v: DataSourceName | str) -> DataSourceName:
        """Ensure DSN is a valid DataSourceName instance."""
        if isinstance(v, str):
            v = DataSourceName.parse(v)

        if not isinstance(v, DataSourceName):
            raise ValueError("dsn must be a valid DataSourceName instance or a string that can be parsed into one.")

        return v

    
    @property
    def driver(self) -> str: return self.dsn.driver
    
    @driver.setter
    def driver(self, value: str) -> None: self.dsn.driver = value
    
    @property
    def username(self) -> str: return self.dsn.username
    
    @username.setter
    def username(self, value: str) -> None: self.dsn.username = value
    
    
    @property
    def password(self) -> str | None: return self.dsn.password.get_secret_value() if self.dsn.password else None
    
    @password.setter
    def password(self, value: str | None) -> None: self.dsn.password = SecretStr(value) if value else None

    @property
    def host(self) -> str: return self.dsn.hostname
    
    
    @host.setter
    def host(self, value: str) -> None: self.dsn.hostname = value

    @property
    def port(self) -> int: return self.dsn.port
    @port.setter
    def port(self, value: int) -> None: self.dsn.port = value
    
    @property
    def database(self) -> str: return self.dsn.database if self.dsn.database else ""
    @database.setter
    def database(self, value: str) -> None: self.dsn.database = value

    @property
    def query(self) -> dict[str, str] | None: return self.dsn.query

    @classmethod
    def from_name_and_dsn(cls, name: str, dsn:str) -> Self:
        """Create a DatabaseConnection instance from a name and DSN string or DataSourceName."""
        return cls.model_validate({
            "name": name,
            "dsn": dsn
        })


    async def sqlalchemy_dispose_async_engine(self) -> None:
        """Dispose the SQLAlchemy async engine if it exists."""
        if self._sqlalchemy_async_engine and isinstance(self._sqlalchemy_async_engine, AsyncEngine):
            await self._sqlalchemy_async_engine.dispose()
            self._sqlalchemy_async_engine = None
    
    async def sqlalchemy_async_engine(self) -> AsyncEngine:
        """Get or create the SQLAlchemy async engine for this connection."""
        if not self._sqlalchemy_async_engine:
            
            # Map user settings to valid SQLAlchemy async engine kwargs
            engine_kwargs = {
                "echo": self.echo,
                # "encoding": self.encoding,  # Removed: asyncpg does not support this argument
                "pool_size": self.pool_min_connections, 
                "max_overflow": self.pool_max_overflow, 
                "pool_timeout": self.connection_timeout,
                "pool_recycle": self.pool_recycle_time,
                "pool_pre_ping": self.pool_pre_ping,
                "pool_use_lifo": False,  # FIFO by default, could be exposed if needed
                "future": True
            }

            # Remove None values so SQLAlchemy defaults are used
            engine_kwargs = {k: v for k, v in engine_kwargs.items() if v is not None}

            self._sqlalchemy_async_engine = create_async_engine( str(self.dsn), **engine_kwargs )

        return self._sqlalchemy_async_engine



    @asynccontextmanager
    async def sqlalchemy_transaction(
        self, 
        isolation_level: Literal["READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"] | None = None
    ) -> AsyncGenerator[AsyncConnection, None]:
        """
        Async context manager for a SQLAlchemy async transaction.

        Args:
            isolation_level: Optional transaction isolation level.

        Yields:
            AsyncConnection with an active transaction (committed or rolled back on exit).
        """
        engine = await self.sqlalchemy_async_engine()
        async with engine.connect() as conn:
            if isolation_level is not None:
                await conn.execution_options(isolation_level=isolation_level)
            async with conn.begin():
                yield conn
