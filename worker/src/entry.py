from workers import WorkerEntrypoint


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # Lazy-import FastAPI app to avoid snapshot serialization issues
        # with vendored packages (anyio/starlette create JS native functions)
        import asgi
        from app import app
        return await asgi.fetch(app, request, self.env)
