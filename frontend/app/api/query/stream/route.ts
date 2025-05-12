import { NextRequest, NextResponse } from 'next/server';

// POST /api/query/stream - Stream a response for a cybersecurity query
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, plugin_id } = body;

    console.log('Stream API request:', { query, plugin_id });

    // Forward the request to the FastAPI backend streaming endpoint
    const backendResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/query/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        plugin_id,
      }),
    });

    console.log('Backend response status:', backendResponse.status);

    if (!backendResponse.ok) {
      let errorMessage = 'Failed to stream response';
      try {
        const errorData = await backendResponse.json();
        errorMessage = errorData.detail || errorMessage;
      } catch (e) {
        console.error('Error parsing error response:', e);
      }
      
      console.error('Stream error:', errorMessage);
      
      return NextResponse.json(
        { error: errorMessage },
        { status: backendResponse.status }
      );
    }

    // Create a TransformStream to forward the streamed response
    const { readable, writable } = new TransformStream();
    
    // Process the stream from the backend
    const reader = backendResponse.body?.getReader();
    const writer = writable.getWriter();
    
    if (reader) {
      // Start reading the stream
      const processStream = async () => {
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              await writer.close();
              break;
            }
            // Forward the chunk to the client
            await writer.write(value);
          }
        } catch (error) {
          console.error('Error processing stream:', error);
          await writer.abort(error);
        }
      };
      
      // Start processing without waiting
      processStream();
    }
    
    // Return the readable stream to the client
    return new NextResponse(readable, {
      headers: {
        'Content-Type': 'application/x-ndjson',
      },
    });
  } catch (error) {
    console.error('Error streaming response:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to stream response' },
      { status: 500 }
    );
  }
}
