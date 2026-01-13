/**
 * Example Firebase Cloud Function (Node.js) that triggers on Auth user creation
 * and calls the Django backend to create a Lecturer profile automatically.
 *
 * Note: this is an example. Deploying functions requires firebase-tools and proper IAM.
 */

const functions = require('firebase-functions');
const admin = require('firebase-admin');
const fetch = require('node-fetch');
admin.initializeApp();

exports.createLecturerProfile = functions.auth.user().onCreate(async (user) => {
  // Only proceed if email verified
  if (!user.email || !user.emailVerified) return null;

  const payload = {
    uid: user.uid,
    email: user.email,
    name: user.displayName || '',
  };

  // Call your backend endpoint (configure URL and API key in environment)
  const backendUrl = process.env.LEC_BACKEND_CREATE_URL;
  const apiKey = process.env.LEC_BACKEND_API_KEY;

  if (!backendUrl) return null;

  try {
    await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-KEY': apiKey || '',
      },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    console.error('Failed to call backend:', err);
  }

  return null;
});