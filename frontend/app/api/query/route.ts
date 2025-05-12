import { NextRequest, NextResponse } from 'next/server';

// POST /api/query - Process a cybersecurity query
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, plugin_id } = body;

    // Forward the request to the FastAPI backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/query/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        plugin_id,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to process query' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error processing query:', error);
    return NextResponse.json(
      { error: 'Failed to process query' },
      { status: 500 }
    );
  }
}
