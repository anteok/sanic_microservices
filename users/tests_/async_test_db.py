import asyncio
import os

from time import sleep

import pytest
from sqlalchemy import create_engine

from backends.db_.db_connector import AsyncPSQLConnector
from tables import metadata


class BaseAsyncDatabaseTest:
    PSQL_URI = os.getenv('PSQL_TEST_URL')
    test_db = AsyncPSQLConnector(PSQL_URI).db

    @pytest.fixture(scope="function")
    def event_loop(self):
        """
        Override event loop for using in function scope.
        """
        loop = asyncio.get_event_loop()
        yield loop
        loop.close()

    @pytest.fixture(autouse=True, scope="function")
    async def create_test_database(self):
        """
        Fixture for creating and closing connection.
        """
        # Create test databases
        try:
            await self.test_db.connect()
        except ConnectionRefusedError:
            sleep(2)
            await self.test_db.connect()
        engine = create_engine(self.PSQL_URI)
        metadata.drop_all(engine)
        metadata.create_all(engine)
        # Run the test suite
        yield
        # Drop test databases
        await self.test_db.disconnect()
        metadata.drop_all(engine)

    @staticmethod
    def sync_exec(coro):
        """
        Function for running coroutines in sync code.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
