const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const Dealership = require('./dealership');
const Review = require('./review');

const app = express();
const port = Number(process.env.PORT || 3030);
const mongoUri = process.env.MONGO_URL || 'mongodb://localhost:27017/dealershipsDB';
const seedDealers = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/dealerships.json'))).dealerships;
const seedReviews = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/reviews.json'))).reviews;
let useMongo = false;
let localReviews = [...seedReviews];

app.use(cors());
app.use(express.json());

const clean = (value) => {
  if (Array.isArray(value)) return value.map(clean);
  const { _id, __v, ...rest } = value.toObject ? value.toObject() : value;
  return rest;
};

async function dealers(filter = {}) {
  return useMongo ? (await Dealership.find(filter).lean()).map(clean) :
    seedDealers.filter((dealer) => Object.entries(filter).every(([key, value]) => dealer[key] === value));
}

async function reviews(filter = {}) {
  return useMongo ? (await Review.find(filter).lean()).map(clean) :
    localReviews.filter((review) => Object.entries(filter).every(([key, value]) => review[key] === value));
}

const route = (handler) => async (req, res) => {
  try { res.json(await handler(req)); }
  catch (error) { res.status(500).json({ error: error.message }); }
};

app.get('/', (_req, res) => res.send('Welcome to the Dealership API'));
app.get('/fetchReviews', route(() => reviews()));
app.get('/fetchReviews/dealer/:id', route((req) => reviews({ dealership: Number(req.params.id) })));
app.get('/fetchDealers', route(() => dealers()));
app.get('/fetchDealers/:state', route((req) => req.params.state === 'All' ? dealers() : dealers({ state: req.params.state })));
app.get('/fetchDealer/:id', route((req) => dealers({ id: Number(req.params.id) })));

app.post('/insert_review', async (req, res) => {
  const data = req.body;
  const required = ['name', 'dealership', 'review', 'purchase_date', 'car_make', 'car_model', 'car_year'];
  if (required.some((field) => !data[field])) {
    return res.status(400).json({ error: 'Missing review fields' });
  }
  try {
    const allReviews = await reviews();
    const review = {
      id: Math.max(0, ...allReviews.map((item) => Number(item.id))) + 1,
      user_id: Number(data.user_id) || undefined,
      name: String(data.name),
      dealership: Number(data.dealership),
      review: String(data.review),
      time: data.time || new Date().toISOString(),
      purchase: Boolean(data.purchase),
      purchase_date: String(data.purchase_date),
      car_make: String(data.car_make),
      car_model: String(data.car_model),
      car_year: Number(data.car_year),
    };
    if (useMongo) await Review.create(review);
    else localReviews.push(review);
    return res.status(201).json(review);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
});

async function start() {
  try {
    await mongoose.connect(mongoUri, { serverSelectionTimeoutMS: 2500 });
    useMongo = true;
    if (await Dealership.countDocuments() === 0) await Dealership.insertMany(seedDealers);
    if (await Review.countDocuments() === 0) await Review.insertMany(seedReviews);
    console.log('Connected to MongoDB');
  } catch (error) {
    console.warn(`MongoDB unavailable; using sample data in memory: ${error.message}`);
  }
  app.listen(port, () => console.log(`Dealership API listening on port ${port}`));
}

if (require.main === module) start();
module.exports = { app, start };
