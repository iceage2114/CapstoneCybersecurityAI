import { NextRequest, NextResponse } from 'next/server';

// GET /api/plugins - Get all plugins
export async function GET(request: NextRequest) {
  try {
    // Forward the request to the FastAPI backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/plugins`);
    
    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch plugins' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching plugins:', error);
    return NextResponse.json(
      { error: 'Failed to fetch plugins' },
      { status: 500 }
    );
  }
}

// POST /api/plugins - Create a new plugin
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Forward the request to the FastAPI backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/plugins`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to create plugin' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 201 });
  } catch (error) {
    console.error('Error creating plugin:', error);
    return NextResponse.json(
      { error: 'Failed to create plugin' },
      { status: 500 }
    );
  }
}
