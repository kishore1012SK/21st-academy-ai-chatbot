# 21st Academy — Career Mapping Workshop Landing Page

A professional landing page for the Career Mapping Workshop by 21st Academy.

---

## 📁 Project Structure

```
career-mapping-workshop/
├── index.html          ← Main page
├── css/
│   └── style.css       ← All styles
├── js/
│   ├── main.js         ← Navbar, scroll, animations, poster download
│   └── chatbot.js      ← AI chatbot (Anthropic Claude API)
└── README.md
```

---

## 🚀 How to Open

1. Open the folder in **VS Code**
2. Right-click `index.html` → **Open with Live Server** (install "Live Server" extension if needed)
3. Or just double-click `index.html` to open in your browser

---

## ⚙️ Two Things to Customize

### 1. Google Form Link
Open `index.html` and find this line (around line 160):

```html
href="https://forms.google.com/your-form-link-here"
```

Replace `your-form-link-here` with your actual Google Form URL.

### 2. Video Link
Open `index.html` and find the `<iframe>` tag in the VIDEO SECTION (around line 140):

```html
src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1"
```

Replace the YouTube video ID (`dQw4w9WgXcQ`) with your actual video ID.
- Example: if your YouTube link is `https://youtu.be/ABC123xyz`, use `ABC123xyz`
- For AI-generated video: upload to YouTube (unlisted) and paste the embed ID

---

## 🤖 AI Chatbot

The chatbot uses the **Anthropic Claude API** directly from the browser.

- It's pre-loaded with all workshop details
- Answers questions about the date, venue, benefits, registration, etc.
- Falls back gracefully if offline

> **Note:** The chatbot works automatically in Claude.ai's artifact environment.
> For standalone deployment (Vercel/Netlify), you'll need a backend proxy to protect your API key.

---

## 🌐 Deploying to Vercel (Free)

1. Create a free account at [vercel.com](https://vercel.com)
2. Drag and drop this folder into Vercel dashboard
3. Click **Deploy** — done!

Or use Netlify:
1. Go to [netlify.com](https://netlify.com) → drag folder → deploy

---

## 🎨 Features

- ✅ Sticky navbar with scroll effect
- ✅ Hero section with event details
- ✅ What You'll Gain cards with hover effects
- ✅ Benefits section with stats board
- ✅ Video section (YouTube embed on click)
- ✅ 3 downloadable event posters (canvas-generated)
- ✅ Registration section with Google Form link
- ✅ AI-powered chatbot with quick replies
- ✅ Fully responsive (mobile, tablet, desktop)
- ✅ Smooth scroll reveal animations

---

## 📞 Contact
- Phone: +91 99 44 74 7090
- Email: admin@21stacademy.in
