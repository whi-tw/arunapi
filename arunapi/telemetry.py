from typing import Tuple

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    MetricReader,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from .settings import Settings


def _providers(
    settings: Settings, metric_reader: MetricReader
) -> Tuple[TracerProvider, MeterProvider]:
    resource = Resource(attributes={SERVICE_NAME: settings.name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    return tracer_provider, meter_provider


def console(settings: Settings):
    metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())

    tracer_provider, meter_provider = _providers(settings, metric_reader)

    trace_processor = BatchSpanProcessor(ConsoleSpanExporter())
    tracer_provider.add_span_processor(trace_processor)


def jaeger_grpc(settings: Settings):
    from opentelemetry.exporter.jaeger.proto.grpc import JaegerExporter

    metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())

    tracer_provider, meter_provider = _providers(settings, metric_reader)

    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                collector_endpoint=settings.telemetry_jaeger_grpc_endpoint,
                insecure=True,
            )
        )
    )


def jaeger_thrift(settings: Settings):
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter

    metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())

    tracer_provider, meter_provider = _providers(settings, metric_reader)

    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(collector_endpoint=settings.telemetry_jaeger_thrift_url)
        )
    )
