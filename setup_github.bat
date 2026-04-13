@echo off
echo ========================================
echo  Voting Portal - GitHub Setup Script
echo ========================================
echo.

echo Step 1: Checking Git installation...
git --version
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    echo Then run this script again.
    pause
    exit /b 1
)

echo Git is installed! Continuing...
echo.

echo Step 2: Initializing Git repository...
cd /d "c:\Users\sashw\OneDrive\Desktop\CODE\voting_portal"
git init
echo.

echo Step 3: Adding all files to Git...
git add .
echo.

echo Step 4: Making initial commit...
git commit -m "Initial commit: Complete Indian Election Voting Portal

Features added:
- Secure user registration with Aadhaar authentication
- Age verification and eligibility checking
- Admin dashboard with election management
- Automated voter generator with realistic data
- Real-time vote monitoring dashboard
- Enhanced results display with winner animations
- Past elections archive
- Excel data export functionality
- SQLite database storage
- Responsive web interface

Technical stack:
- Flask web framework
- SQLite databases
- HTML/CSS/JavaScript frontend
- Python threading for background processing"
echo.

echo Step 5: Setting up GitHub repository...
echo Please create a new repository on GitHub with these details:
echo Repository name: voting-portal
echo Description: Complete Indian Election Voting Portal with automated voter generation and real-time monitoring
echo Make it Public
echo.
echo After creating the repository, copy the repository URL and paste it below:
set /p repo_url="Enter GitHub repository URL: "
echo.

echo Step 6: Adding GitHub remote...
git remote add origin %repo_url%
echo.

echo Step 7: Pushing to GitHub...
git push -u origin master
echo.

echo ========================================
echo SUCCESS! Project uploaded to GitHub!
echo ========================================
echo.
echo Your voting portal is now live on GitHub!
echo Repository URL: %repo_url%
echo.
echo Next steps:
echo 1. Visit your GitHub repository
echo 2. Add a description and topics
echo 3. Enable GitHub Pages if desired
echo 4. Share with others!
echo.
pause