# AI Land Optimization - Frontend

React frontend for the AI Land Optimization system with intelligent floor plan generation.

## Features

- **Calculate Buildable Area**: Check land feasibility and buildable area calculations
- **Full Optimization**: Generate optimized floor plans with AI
- **8 Sample Scenarios**: Pre-loaded test data (Tiny to Luxury plots)
- **Real-time Results**: Instant feedback with buildable area analysis
- **Dual Visualizations**: Land plot + Detailed floor plan outputs
- **Responsive Design**: Works on desktop, tablet, and mobile

## Tech Stack

- **React 18** - UI Framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client
- **Backend API**: http://localhost:8000

## Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

## Installation

```bash
# Install dependencies
npm install
```

## Running the Application

```bash
# Start development server (runs on http://localhost:3000)
npm run dev
```

The frontend will automatically proxy API requests to the backend at http://localhost:8000.

## Building for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── LandInputForm.jsx
│   │   ├── BuildableAreaResults.jsx
│   │   ├── VisualizationDisplay.jsx
│   │   ├── LoadingSpinner.jsx
│   │   └── Layout.jsx
│   ├── pages/             # Page components
│   │   ├── HomePage.jsx
│   │   ├── CalculatePage.jsx
│   │   └── OptimizePage.jsx
│   ├── services/          # API integration
│   │   └── api.js
│   ├── data/              # Sample data
│   │   └── sampleLands.js
│   ├── App.jsx            # Root component with routing
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── index.html
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
└── package.json
```

## API Integration

The frontend connects to the backend using three main endpoints:

### 1. Calculate Buildable Area
```
POST /api/v1/optimization/calculate-buildable-area
```
Returns buildable area analysis and feasibility check.

### 2. Run Optimization
```
POST /api/v1/optimization/optimize?save_to_db=false
```
Generates optimized floor plan with two visualizations.

### 3. Get Visualization
```
GET /api/v1/optimization/visualization/{filename}
```
Downloads generated image files.

## Sample Data

The frontend includes 8 pre-configured sample scenarios:

1. **Tiny Plot** (10m×8m) - FAILS - Not enough space
2. **Small Plot** (15m×12m) - TIGHT FIT - Room reduction needed
3. **Medium Plot** (20m×15m) - COMFORTABLE - All rooms fit
4. **Large Plot** (25m×20m) - SPACIOUS - Plenty of extra space
5. **Luxury Plot** (30m×25m) - ESTATE - Enormous extra space
6. **Narrow Plot** (25m×10m) - CHALLENGING - Linear layout
7. **Wide Plot** (15m×20m) - COMFORTABLE - Good flexibility
8. **Square Plot** (18m×18m) - OPTIMAL - Best efficiency

## Features Walkthrough

### Calculate Page
- Input land dimensions and room requirements
- Load sample data from dropdown
- Get instant buildable area analysis
- See feasibility status (will fit / not enough space)
- View requested vs optimized room counts
- See setback details and usable area

### Optimize Page
- Same inputs as Calculate page
- Runs full genetic algorithm optimization
- Generates two professional visualizations:
  - OUTPUT 1: Land plot with buildable area highlighted
  - OUTPUT 2: Complete floor plan with rooms, walls, doors, fixtures
- Shows optimization statistics (execution time, fitness score)
- Download buttons for both images

## Configuration

### Backend API URL
Edit `vite.config.js` to change the backend URL:

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Change this
        changeOrigin: true,
      },
    },
  },
})
```

### Styling
Modify `tailwind.config.js` to customize colors and theme.

## Troubleshooting

### Backend Connection Issues
- Ensure backend is running: `http://localhost:8000`
- Check backend logs for errors
- Verify CORS is configured on backend

### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use
Change the port in `vite.config.js`:
```javascript
server: {
  port: 3001,  // Change port
}
```

## Development

### Hot Reload
Vite provides instant hot module replacement (HMR). Changes appear immediately without full page refresh.

### Component Development
All components are in `src/components/`. Follow the existing patterns:
- Functional components with hooks
- Props for data passing
- TailwindCSS for styling
- Responsive design (mobile-first)

### Adding New Features
1. Create component in `src/components/`
2. Add page in `src/pages/` if needed
3. Update routes in `src/App.jsx`
4. Add API method in `src/services/api.js`

## License

This is part of the AI Land Optimization research project.

## Contact

For issues or questions, refer to the main project documentation.
