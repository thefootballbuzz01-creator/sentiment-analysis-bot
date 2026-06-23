const express = require('express');
const axios = require('axios');
const { SentimentAnalyzer } = require('natural');
const natural = require('natural');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static('public'));

// Simple sentiment analysis using natural library
const analyzer = new natural.SentimentAnalyzer('English', natural.PorterStemmer, 'afinn');

function analyzeSentiment(text) {
  if (!text || text.length < 3) {
    return { label: 'Neutral', score: 0 };
  }

  const tokens = text.toLowerCase().split(/\s+/);
  const score = analyzer.getSentiment(tokens);

  let label = 'Neutral';
  if (score > 0.1) label = 'Positive';
  if (score < -0.1) label = 'Negative';

  return { label, score: Math.round(score * 100) / 100 };
}

// Mock data for demo (since we can't actually scrape in this environment)
function generateMockComments(source, count = 10) {
  const sampleComments = {
    positive: [
      "This is amazing! Love it!",
      "Best thing I've seen all day",
      "Absolutely fantastic work!",
      "This made me so happy",
      "Wonderful! Can't wait for more",
      "Incredible quality!",
      "This is perfect!",
      "Outstanding!",
      "Loved every second of this",
      "This brightened my day"
    ],
    negative: [
      "This is terrible",
      "Worst thing ever",
      "Absolutely disappointed",
      "Complete waste of time",
      "Really bad quality",
      "Hate this",
      "Awful experience",
      "Not happy with this",
      "This sucks",
      "Extremely disappointed"
    ],
    neutral: [
      "This is okay",
      "Average content",
      "Nothing special",
      "It's fine",
      "Not bad",
      "Could be better",
      "Interesting",
      "Some good points",
      "Mixed feelings",
      "It works"
    ]
  };

  const comments = [];
  const allComments = [...sampleComments.positive, ...sampleComments.negative, ...sampleComments.neutral];

  for (let i = 0; i < count; i++) {
    const text = allComments[Math.floor(Math.random() * allComments.length)];
    const sentiment = analyzeSentiment(text);
    comments.push({
      author: `User_${Math.floor(Math.random() * 10000)}`,
      text,
      ...sentiment,
      source
    });
  }

  return comments;
}

app.post('/api/analyze', (req, res) => {
  try {
    const { youtubeUrls, redditSubreddits } = req.body;

    let allComments = [];
    let stats = {
      youtube: { Positive: 0, Negative: 0, Neutral: 0, total: 0 },
      reddit: { Positive: 0, Negative: 0, Neutral: 0, total: 0 }
    };

    // Generate mock YouTube comments
    if (youtubeUrls && youtubeUrls.length > 0) {
      const youtubeComments = generateMockComments('YouTube', 50);
      allComments = allComments.concat(youtubeComments);

      youtubeComments.forEach(c => {
        stats.youtube[c.label]++;
        stats.youtube.total++;
      });
    }

    // Generate mock Reddit comments
    if (redditSubreddits && redditSubreddits.length > 0) {
      const redditComments = generateMockComments('Reddit', 50);
      allComments = allComments.concat(redditComments);

      redditComments.forEach(c => {
        stats.reddit[c.label]++;
        stats.reddit.total++;
      });
    }

    // Sort by sentiment score
    const topPositive = allComments
      .filter(c => c.label === 'Positive')
      .sort((a, b) => b.score - a.score)
      .slice(0, 10);

    const topNegative = allComments
      .filter(c => c.label === 'Negative')
      .sort((a, b) => a.score - b.score)
      .slice(0, 10);

    res.json({
      success: true,
      stats,
      topPositive,
      topNegative,
      totalComments: allComments.length,
      timestamp: new Date().toLocaleString()
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`  🎯 SENTIMENT ANALYZER`);
  console.log(`${'='.repeat(60)}`);
  console.log(`\n  ✅ Server running at http://localhost:${PORT}`);
  console.log(`\n  📌 Open in your browser and start analyzing!\n`);
  console.log(`${'='.repeat(60)}\n`);
});
