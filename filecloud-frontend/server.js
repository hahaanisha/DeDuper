const express = require('express');
const path = require('path');
const app = express();
const PORT = 5501;

// Middleware to parse JSON bodies
app.use(express.json());

// Serve static files
app.use(express.static('public'));

// Serve the index.html file for the root path
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Proxy endpoint for file deletion (for local development)
app.delete('/api/delete', async (req, res) => {
  try {
    const { fileHash, userID } = req.body;

    // Dynamically import node-fetch
    const fetch = (await import('node-fetch')).default;

    // Call the AWS Lambda function
    const response = await fetch('https://ly7nl5fawc.execute-api.us-east-1.amazonaws.com/delete', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ fileHash, userID })
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Error forwarding delete request:', error);
    res.status(500).json({ error: 'Failed to delete file' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
