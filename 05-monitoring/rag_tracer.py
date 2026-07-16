from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from sqlitespanexporter import SQLiteSpanExporter

provider = TracerProvider()
provider.add_span_processor(
    SimpleSpanProcessor(SQLiteSpanExporter("traces.db"))
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

from rag_helper import RAGBase

class RAGTraced(RAGBase):
    def rag(self, *args, **kwargs):
        with tracer.start_as_current_span("rag") as span:
            span.set_attribute("component", "rag")
            return super().rag(*args, **kwargs)

    def llm(self, *args, **kwargs):
        with tracer.start_as_current_span("llm") as span:
            response = super().llm(*args, **kwargs)
            
            span.set_attribute("component", "llm")
            span.set_attribute("input_tokens", response.usage.input_tokens)
            span.set_attribute("output_tokens", response.usage.output_tokens)
            
            return response
    
    def search(self, *args, **kwargs):
        with tracer.start_as_current_span("search") as span:
            span.set_attribute("component", "search")
            return super().search(*args, **kwargs)