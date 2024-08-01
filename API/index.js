const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const port = 4000;
const FLASK_API_URL = 'http://localhost:5000';

app.use(bodyParser.json());

const allowedOrigins = ['http://localhost:5173', 'http://localhost:5174'];

app.use(cors({
    origin: function (origin, callback) {
        if (!origin) return callback(null, true);
        if (allowedOrigins.indexOf(origin) === -1) {
            const msg = 'The CORS policy for this site does not ' +
                'allow access from the specified Origin.';
            return callback(new Error(msg), false);
        }
        return callback(null, true);
    }
}));

app.options('*', cors());

app.post('/interview', async (req, res) => {
    try {
        const { user_input, filename, question, answer, initial_questions, level } = req.body;

        if (level === 0 && !user_input) {
            return res.status(400).json({ error: "Invalid input, 'user_input' is required." });
        } else if ((level === 1 || level === 2) && (!filename || !answer)) {
            return res.status(400).json({ error: "Invalid input, 'filename', 'question', and 'answer' are required." });
        }

        const response = await axios.post(`${FLASK_API_URL}/interview`, { user_input, filename, question, answer, initial_questions, level });
        res.json(response.data);
    } catch (error) {
        console.error("Error handling interview:", error.message);
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Node.js server running on http://localhost:${port}`);
});
