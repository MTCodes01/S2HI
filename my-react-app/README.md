# S2HI Frontend

The React-based frontend for the S2HI (AI Samasya) learning disability assessment platform.

## Overview
This application provides an interactive, gamified interface for children to complete assessments. It communicates with the Django backend to serve adaptive questions and display results.

## Tech Stack
- **Framework**: React 18+
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: CSS Modules / Standard CSS
- **Routing**: React Router DOM

## Project Structure
```
src/
├── components/   # Reusable UI components
├── pages/        # Main application pages (Dashboard, Assessment, etc.)
├── services/     # API integration logic
├── styles/       # Global styles and themes
├── types/        # TypeScript type definitions
├── App.tsx       # Main app component and routing
└── main.tsx      # Entry point
```

## Setup & Run

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation
1. Navigate to the project directory:
   ```bash
   cd my-react-app
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

### Development
Start the development server:
```bash
npm run dev
```
The app will happen at `http://localhost:5173`.
