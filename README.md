# Voting Portal

A comprehensive online voting system for Indian elections with secure user registration, admin controls, automated voter generation, real-time monitoring, and enhanced results display.

## Features

### For Citizens:
- **Secure Registration**: Register with Aadhaar number, personal details, and auto-generated PIN
- **Age Verification**: Automatic eligibility checking based on date of birth
- **Secure Voting**: Cast votes only if eligible (18+ years)
- **Real-time Status**: Check voting status and results

### For Administrators:
- **Special Admin Access**: Login with predefined credentials
- **Election Management**: Open/close voting periods
- **Vote Counting**: Start and complete vote counting process
- **Data Analysis**: View and download comprehensive election data
- **Election Commission Mode**: Dedicated interface for election officials
- **🤖 Automated Voter Generator**: Generate random voters and votes for testing
- **📊 Real-time Monitoring**: Live vote counting and statistics dashboard
- **🏆 Enhanced Results**: Winner animations and detailed party rankings
- **📚 Past Elections Archive**: View historical election data

### Automated Features:
- **Smart Voter Generator**: Creates realistic Indian voter profiles with random names, ages, cities, and Aadhaar numbers
- **Configurable Probabilities**: BJP (55%), Congress (20%), AAP (15%), Other Parties (9%), Invalid (1%)
- **Real-time Updates**: Live dashboard showing vote counts as they happen
- **Background Processing**: Non-blocking voter generation that runs in parallel

## Setup Instructions

### Prerequisites:
- Python 3.7+
- Flask web framework
- SQLite (built-in with Python)

### Install Dependencies:
```bash
pip install flask pandas openpyxl
```

### Run the Application:
```bash
cd voting_portal
python app.py
```

### Access the Portal:
- Open your browser and go to `http://localhost:5000`
- Register as a new user or login with existing credentials

## Admin Credentials

- **Admin**: Aadhaar: `452545254525`, PIN: `4525`
- **Election Commission**: Aadhaar: `111111111111`, PIN: `1111`

## Database Structure

The application creates three SQLite databases in the `databases/` folder:

1. **users.db**: User registration data
2. **votes.db**: Vote records
3. **invalid_attempts.db**: Records of ineligible voting attempts

## Security Features

- Aadhaar-based authentication
- 4-digit PIN system
- Age verification
- Session management
- Secure database storage

## File Structure

```
voting_portal/
├── app.py                    # Main Flask application with all routes
├── voter_generator.py        # Automated voter generation system
├── templates/               # HTML templates
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── vote.html
│   ├── voting_closed.html
│   ├── admin_dashboard.html
│   ├── results.html
│   ├── realtime_votes.html
│   └── past_elections.html
├── static/                  # Static assets
│   ├── css/
│   │   └── style.css       # Enhanced styling with animations
│   └── js/
│       └── script.js       # Client-side validation
├── databases/               # SQLite databases (auto-created)
│   ├── users.db
│   ├── votes.db
│   └── invalid_attempts.db
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── QUICK_START.md          # Quick start guide for new features
```

## Usage

### For Regular Users:
1. **User Registration**: New users register with personal details
2. **Login**: Users login with Aadhaar and PIN
3. **Voting**: Eligible users can cast their votes
4. **Check Results**: View election results after voting closes

### For Administrators:
1. **Admin Login**: Use special admin credentials
2. **Election Control**: Open/close voting periods
3. **Automated Testing**: Start voter generator for testing
4. **Real-time Monitoring**: Watch live vote statistics
5. **Data Management**: View and export election data
6. **Results Management**: Initiate vote counting and view results

### Advanced Features:
- **Real-time Dashboard**: Monitor votes as they come in
- **Past Elections**: Review historical election data
- **Automated Generation**: Test with realistic voter data
- **Enhanced Results**: View animated winner displays

## Automated Voter Generator

The system includes a sophisticated automated voter generation system for testing and demonstration:

### Features:
- **Realistic Data Generation**: Creates authentic Indian names, cities, phone numbers, and Aadhaar numbers
- **Configurable Probabilities**: 
  - BJP: 55%
  - Congress: 20%
  - AAP: 15%
  - Other Parties: 9%
  - Invalid Votes: 1%
- **Speed Control**: Generates ~20 voters per second
- **Background Processing**: Runs without blocking the UI
- **Smart Controls**: Only runs when voting is open, auto-stops when voting closes

### Usage:
1. Login to admin dashboard
2. Navigate to "🤖 Automatic Voter Generator" section
3. Click "Start Auto-Generator"
4. Monitor real-time statistics
5. Click "Stop Auto-Generator" when done

## Real-time Monitoring

### Live Dashboard Features:
- **Real-time Vote Counter**: Updates every second showing current vote totals
- **Party-wise Statistics**: Live percentage calculations for each party
- **Voter Generation Status**: Shows generator activity and voter count
- **Election Status**: Current voting period status (Open/Closed)

### Access:
- Available in admin dashboard
- Automatic updates without page refresh
- Historical data preservation

## Enhanced Results Display

### Winner Animation:
- **Spectacular Banner**: Large animated winner announcement
- **Trophy Animation**: Bouncing trophy icon with scaling effects
- **Shimmer Effect**: Golden glow bars over the winner banner
- **Pulsing Animation**: Continuous banner pulsing for emphasis

### Rankings System:
- **🥇 Winner**: Highlighted with golden styling
- **🥈 2nd Place**: Silver badge and styling
- **🥉 3rd Place**: Bronze badge and styling
- **Detailed Statistics**: Vote counts and percentages for all parties

## Past Elections Archive

View historical election data with:
- **Election History**: Previous election results and dates
- **Comparative Analysis**: Vote trends across elections
- **Data Preservation**: All past election data maintained in database

## Data Export

Administrators can download comprehensive data in Excel format:
- **User Registrations**: Complete voter database with demographics
- **Vote Records**: All cast votes with timestamps and party selections
- **Invalid Attempts**: Records of ineligible voting attempts
- **Election Statistics**: Summary reports and analytics

## Technical Architecture

### Backend:
- **Flask Framework**: Lightweight web framework for routing and session management
- **SQLite Databases**: Local database storage for data persistence
- **Threading**: Background processing for automated voter generation
- **Pandas**: Data manipulation and Excel export functionality

### Frontend:
- **HTML5/CSS3**: Responsive design with modern styling
- **JavaScript**: Client-side form validation and dynamic updates
- **Jinja2 Templates**: Server-side templating for dynamic content

### Security Features:
- Aadhaar-based authentication system
- 4-digit PIN security
- Age verification (18+ requirement)
- Session management and protection
- Secure database storage
- Input validation and sanitization

### Database Structure:

The application creates three SQLite databases:

1. **users.db**: User registration data
   - Aadhaar numbers, names, DOB, contact info, PINs
   
2. **votes.db**: Vote records
   - Voter Aadhaar, party selection, timestamp, election ID
   
3. **invalid_attempts.db**: Records of ineligible voting attempts
   - Attempt details, reasons for rejection

## Election Management

- **Election Identification**: Unique 3-digit election numbers
- **Voting Periods**: Admin-controlled open/close functionality
- **Vote Counting**: Manual initiation after voting closes
- **Results Display**: Comprehensive results with winner animations
- **Historical Data**: Past elections archive and comparison