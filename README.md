# Expense Analyzer

A full-stack web application designed to track, manage, and analyze personal expenses. It features a responsive dashboard, mobile-optimized views, and AI-powered insights for financial management.

## Features

*   **Interactive Dashboard:** View spending trends and balances.
*   **Mobile Variant:** A specialized, mobile-friendly interface secured with a dedicated PIN.
*   **AI Insights:** Integrates with the Groq API to provide AI-driven analysis of your spending habits and financial data.
*   **Secure Access:** PIN-based authentication for quick yet secure access.
*   **Responsive UI:** Built with Flask and custom HTML/CSS to work seamlessly across desktop and mobile devices.

## Tech Stack

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, JavaScript (Vanilla)
*   **AI Integration:** Groq API
*   **Deployment:** Configured for deployment on Ubuntu-based VMs (EC2/GCP) using Gunicorn and Nginx.

## Local Setup

### Prerequisites

*   Python 3.8+
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_GITHUB_USERNAME/expense-analyzer.git
    cd expense-analyzer
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Create a `.env` file in the root directory and add the necessary configurations:
    ```env
    SECRET_KEY=your_flask_secret_key
    APP_PIN=1234
    APP_VARIANT=desktop # Set to 'mobile' for the mobile UI
    GROQ_API_KEY=your_groq_api_key
    ```

5.  **Run the application:**
    ```bash
    python app.py
    ```

    The app will be available at `http://localhost:5000`.

## Deployment

The application is designed to be deployed using Gunicorn behind an Nginx reverse proxy. GitHub Actions workflows are included (`.github/workflows/`) for automated CI/CD deployments to EC2 or generic VMs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
