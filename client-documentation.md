# Smart Scale WebSocket Server - Client Documentation

This document provides information on how to connect to and use the Smart Scale WebSocket server.

## Server Overview

The server provides real-time updates from a smart scale system, including weight measurements and associated images.

- WebSocket endpoint: `ws://192.168.1.16:8000/ws`
- Image serving endpoint: `http://192.168.1.16:8000/images/[filename]`

## Connecting to the WebSocket

To connect to the WebSocket, use the following code:

```javascript
const ws = new WebSocket('ws://192.168.1.16:8000/ws');
```

## Message Format

The server sends JSON messages with the following structure:

```json
{
  "datetime": "YYYY-MM-DD HH:MM:SS",
  "total_weight": float,
  "total_count": integer,
  "average_weight": float,
  "image_path": "string",
  "image_url": "string"
}
```

- `datetime`: The timestamp of the measurement
- `total_weight`: The total weight measured, in kilograms
- `total_count`: The number of items counted
- `average_weight`: The average weight per item, in kilograms
- `image_path`: The server-side path of the associated image
- `image_url`: The URL to access the image

## Handling Messages

To handle incoming messages:

```javascript
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // Process the data here
};
```

## Displaying Images

To display the image associated with a measurement:

```javascript
if (data.image_url) {
    const imageUrl = `http://192.168.1.16:8000${data.image_url}`;
    // Use this URL to display the image (e.g., in an <img> tag)
}
```

## Error Handling

It's important to handle potential errors:

```javascript
ws.onerror = function(error) {
    console.error('WebSocket Error:', error);
};

ws.onclose = function() {
    console.log('Disconnected from WebSocket server');
    // Implement reconnection logic if needed
};
```

## Example Implementation

Here's a basic example of how to implement a client:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Scale Data Viewer</title>
</head>
<body>
    <div id="data-container"></div>
    <div id="image-container"></div>

    <script>
        const ws = new WebSocket('ws://192.168.1.16:8000/ws');
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            // Update data display
            document.getElementById('data-container').innerHTML = `
                <p>Date: ${data.datetime}</p>
                <p>Total Weight: ${data.total_weight} kg</p>
                <p>Total Count: ${data.total_count}</p>
                <p>Average Weight: ${data.average_weight} kg</p>
            `;

            // Update image
            if (data.image_url) {
                document.getElementById('image-container').innerHTML = 
                    `<img src="http://192.168.1.16:8000${data.image_url}" alt="Smart Scale Image">`;
            }
        };
    </script>
</body>
</html>
```

