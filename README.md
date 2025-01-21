# Millenium Flacon Challenge

This repository contains the work I conducted for the Millennium Falcon Challenge proposed by Dataiku: https://github.com/dataiku/millenium-falcon-challenge

The project involves a FastAPI backend, a React frontend, and a CLI tool to compute the odds that the Millennium Falcon reaches Endor in time based on provided configurations.

## Table of Contents


- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Backend](#backend)
    - [Frontend](#frontend)
    - [CLI](#cli)
- [Usage](#usage)
  - [Running the Backend](#running-the-backend)
  - [Running the Frontend](#running-the-frontend)
  - [Using the CLI](#using-the-cli)
  - [Running unit tests](#running-unit-tests)

## Features

- **FastAPI Backend:** Handles API requests to compute odds based on uploaded configurations.
- **React Frontend:** User-friendly interface to upload `empire.json` files and view results.
- **CLI Tool:** Command-line interface to compute odds directly from the terminal.
- **Logging:** Comprehensive logging for easier debugging and monitoring.
- **Deployment:** Deployed on AWS EC2 with a custom domain.

## Technologies used

- **Backend:**
  - Python 3.13
  - FastAPI
  - Uvicorn
  - SQLite
- **Frontend:**
  - React
  - Vite
  - Tailwind CSS
- **CLI:**
  - Python
- **Deployment:**
  - AWS EC2, Route 53
  - Nginx

 ## Getting started

 ### Prerequisites

 Ensure you have the following installed on your local machine:

- **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Comes with Python installations.
- **Node.js and npm**: [Download Node.js](https://nodejs.org/en/download)

### Installation

Clone the repository:
```
git clone https://github.com/nasr020/millenium-falcon-challenge.git
cd millenium-falcon-challenge
```

#### Backend

Create a virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

Install dependencies

```
pip install -r requirements.txt
```

#### Frontend

Navigate to the frontend directory

```
cd src/frontend
```

Install frontend dependencies
```
npm install
```

#### CLI

Install the cli tool by running
```
pip install .
```
from the root of this project.

## Usage

### Running the Backend

Activate the virtual environment by running
```
source venv/bin/activate
```
from the root of this project.

Run the backend server:
```
uvicorn src.backend.app:app --host 0.0.0.0 --port 8000
```

Test the backend
Open a new terminal window and run:
```
curl http://127.0.0.1:8000/
```
You should receive a response:
```
{"message":"Welcome to the Millennium Falcon Odds API!"}
```

### Running the frontend

Navigate to the frontend directory
```
cd src/frontend
```
Start the frontend development server
```
npm run dev
```
Access the frontend by opening a browser and then going to `http://localhost:5173/`. You can upload `empire.json` files and interact with the backend through the UI.

### Using the CLI

Install the cli tool by running from the root directory:
```
pip install .
```

Example CLI command:
```
give-me-the-odds examples/example1/millennium-falcon.json examples/example1/empire.json
```

### Running unit tests

All of the unit tests can be run using the command `pytest` from the root directory.
