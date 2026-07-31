using System.Net.Http.Json;
using System.Threading.Channels;

namespace DIAZAI.StateTrace.OASIS;

public sealed record StateTraceEvent(
    string trace_id, string event_id, long sequence, DateTimeOffset timestamp,
    string source, string operation, string? actor_id, string? target_id,
    string effect_class, object payload, object metadata);

public sealed class StateTraceSidecar : IAsyncDisposable
{
    private readonly HttpClient _http;
    private readonly Channel<StateTraceEvent> _queue;
    private readonly CancellationTokenSource _stop = new();
    private readonly Task _worker;
    public long Accepted { get; private set; }
    public long Failed { get; private set; }

    public StateTraceSidecar(Uri endpoint, int capacity = 10_000, HttpMessageHandler? handler = null)
    {
        _http = handler is null ? new HttpClient() : new HttpClient(handler);
        _http.BaseAddress = endpoint;
        _queue = Channel.CreateBounded<StateTraceEvent>(new BoundedChannelOptions(capacity) {
            SingleReader = true,
            SingleWriter = false,
            FullMode = BoundedChannelFullMode.DropWrite
        });
        _worker = Task.Run(DrainAsync);
    }

    public bool TryRecord(StateTraceEvent item) => _queue.Writer.TryWrite(item);

    public bool RecordStarOperation(string traceId, long sequence, string operation, string avatarId, object payload, string effectClass = "exact")
    {
        var eventId = $"{traceId}-{sequence:D20}-{operation}";
        return TryRecord(new StateTraceEvent(
            traceId, eventId, sequence, DateTimeOffset.UtcNow,
            "OASIS.STARAPIClient", operation, avatarId, null,
            effectClass, payload,
            new { adapter = "csharp-channel-v1", post_success_callback = true }
        ));
    }

    private async Task DrainAsync()
    {
        await foreach (var item in _queue.Reader.ReadAllAsync(_stop.Token))
        {
            try
            {
                using var response = await _http.PostAsJsonAsync("v1/events", item, cancellationToken: _stop.Token);
                if (response.IsSuccessStatusCode) Accepted++; else Failed++;
            }
            catch (OperationCanceledException) when (_stop.IsCancellationRequested) { break; }
            catch { Failed++; }
        }
    }

    public async ValueTask DisposeAsync()
    {
        _queue.Writer.TryComplete();
        try { await _worker.WaitAsync(TimeSpan.FromSeconds(5)); }
        catch { _stop.Cancel(); }
        _http.Dispose();
        _stop.Dispose();
    }
}
