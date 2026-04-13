import threading
import time
import random
import sqlite3
import os
from datetime import datetime, timedelta

# Indian names database
FIRST_NAMES = [
    'Raj', 'Priya', 'Arjun', 'Ananya', 'Vikram', 'Deepika', 'Arun', 'Zara',
    'Nikhil', 'Pooja', 'Rohan', 'Neha', 'Aditya', 'Divya', 'Karan', 'Isha',
    'Sanjay', 'Meera', 'Amit', 'Tina', 'Ravi', 'Anjali', 'Sandeep', 'Kavya',
    'Ashutosh', 'Swati', 'Varun', 'Shreya', 'Suresh', 'Nisha', 'Akshay', 'Ritika',
    'Mohit', 'Simran', 'Darshan', 'Anushka', 'Harsha', 'Divyendu', 'Prakash', 'Yamini',
    'Avinash', 'Chandni', 'Bhargav', 'Shreya', 'Sameer', 'Sonam', 'Tanvi', 'Rashid',
    'Vikrant', 'Chitra', 'Vaibhav', 'Swara', 'Karthik', 'Natasha', 'Ishant', 'Mahira',
    'Anurag', 'Diya', 'Rajesh', 'Divya', 'Yash', 'Karishma', 'Gaurav', 'Priyanka',
    'Aryan', 'Shraddha', 'Sushant', 'Rani', 'Siddharth', 'Sneha', 'Abhishek', 'Vidya'
]

LAST_NAMES = [
    'Kumar', 'Singh', 'Patel', 'Sharma', 'Reddy', 'Khan', 'Gupta', 'Verma',
    'Desai', 'Nair', 'Iyer', 'Rao', 'Agarwal', 'Chopra', 'Malhotra', 'Sinha',
    'Mishra', 'Bhat', 'Kulkarni', 'Joshi', 'Nambiar', 'Pillai', 'Srivastava', 'Roy',
    'Das', 'Dutta', 'Bose', 'Mukherjee', 'Chowdhury', 'Bhattacharya', 'Dasgupta', 'Ganguly',
    'Pandey', 'Tripathi', 'Maurya', 'Tiwari', 'Yadav', 'Thakur', 'Saxena', 'Saxena',
    'Rawat', 'Pandya', 'Dubey', 'Jain', 'Kapoor', 'Arora', 'Bhatnagar', 'Goel',
    'Mathur', 'Garg', 'Menon', 'Shetty', 'Rao', 'Reddy', 'Deshmukh', 'Patil'
]

CITIES = [
    'Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune',
    'Ahmedabad', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Surat', 'Indore',
    'Thane', 'Bhopal', 'Visakhapatnam', 'Vadodara', 'Ghaziabad', 'Ludhiana'
]

PARTIES = ['BJP', 'Congress', 'AIMIM', 'TMC', 'Samajwadi Party', 'AAP']

class VoterGenerator:
    def __init__(self, db_folder):
        self.db_folder = db_folder
        self.is_running = False
        self.thread = None
        self.voter_count = 0
        
    def get_db_connection(self, db_name):
        db_path = os.path.join(self.db_folder, f'{db_name}.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def generate_random_aadhaar(self):
        """Generate a random 12-digit Aadhaar number"""
        return ''.join([str(random.randint(0, 9)) for _ in range(12)])
    
    def generate_random_dob(self):
        """Generate a random date of birth for voters aged 18-70"""
        today = datetime.today()
        age = random.randint(18, 70)
        random_bday = today.replace(year=today.year - age)
        # Add random days
        random_bday = random_bday - timedelta(days=random.randint(0, 364))
        return random_bday.strftime('%Y-%m-%d')
    
    def generate_voter_data(self):
        """Generate random voter data"""
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        
        dob = self.generate_random_dob()
        aadhaar = self.generate_random_aadhaar()
        city = random.choice(CITIES)
        # Reduce NRI probability from ~50% to 5%
        nri = 'Yes' if random.random() < 0.05 else 'No'
        phone = str(random.randint(6000000000, 9999999999))
        pin = str(random.randint(1000, 9999))
        
        return {
            'name': name,
            'dob': dob,
            'aadhaar': aadhaar,
            'city': city,
            'nri': nri,
            'phone': phone,
            'pin': pin
        }
    
    def calculate_age(self, dob_str):
        """Calculate age from DOB string"""
        birth_date = datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    
    def register_voter(self, voter_data):
        """Register a voter in the database"""
        try:
            conn = self.get_db_connection('users')
            age = self.calculate_age(voter_data['dob'])
            
            conn.execute('''INSERT INTO users (name, dob, age, aadhaar, city, nri, phone, pin)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (voter_data['name'], voter_data['dob'], age, voter_data['aadhaar'],
                         voter_data['city'], voter_data['nri'], voter_data['phone'], voter_data['pin']))
            conn.commit()
            
            # Get the newly registered user ID
            user = conn.execute('SELECT id FROM users WHERE aadhaar = ?', (voter_data['aadhaar'],)).fetchone()
            user_id = user['id']
            conn.close()
            
            return user_id
        except sqlite3.IntegrityError:
            # Aadhaar already exists, try again
            return None
    
    def cast_vote(self, user_id):
        """Cast a random vote with BJP having 55% probability, 1% invalid"""
        rand = random.random()
        
        if rand < 0.55:  # 55% BJP (50-60% range)
            vote = 'BJP'
        elif rand < 0.56:  # 1% invalid (no vote cast)
            return False  # Invalid voter - don't cast vote
        else:
            # Remaining 44% distributed among other parties
            vote = random.choice(['Congress', 'AIMIM', 'TMC', 'Samajwadi Party', 'AAP'])
        
        try:
            conn = self.get_db_connection('users')
            election = conn.execute('SELECT * FROM elections WHERE status = ? ORDER BY id DESC LIMIT 1',
                                   ('open',)).fetchone()
            conn.close()
            
            if not election:
                return False
            
            conn = self.get_db_connection('votes')
            conn.execute('INSERT INTO votes (user_id, election_id, vote) VALUES (?, ?, ?)',
                        (user_id, election['id'], vote))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error casting vote: {e}")
            return False
    
    def check_voting_open(self):
        """Check if voting is currently open"""
        try:
            conn = self.get_db_connection('users')
            election = conn.execute('SELECT status FROM elections ORDER BY id DESC LIMIT 1').fetchone()
            conn.close()
            return election and election['status'] == 'open'
        except Exception as e:
            print(f"Error checking voting status: {e}")
            return False
    
    def generate_voters_loop(self):
        """Main loop for generating voters"""
        print("[VOTER GENERATOR] Started")
        
        while self.is_running:
            # Check if voting is open
            if not self.check_voting_open():
                print("[VOTER GENERATOR] Voting is not open. Waiting...")
                time.sleep(5)
                continue
            
            # Generate and register a voter
            voter_data = self.generate_voter_data()
            user_id = self.register_voter(voter_data)
            
            if user_id:
                # Cast a vote
                if self.cast_vote(user_id):
                    self.voter_count += 1
                    print(f"[VOTER GENERATOR] Voter #{self.voter_count}: {voter_data['name']} (ID: {user_id}) registered and voted")
                else:
                    print(f"[VOTER GENERATOR] Failed to cast vote for {voter_data['name']}")
            else:
                print(f"[VOTER GENERATOR] Failed to register voter (Aadhaar might already exist)")
            
            # Random delay between 0.05 seconds (20 votes per second)
            time.sleep(0.05)
    
    def start(self):
        """Start the voter generator in a background thread"""
        if not self.is_running:
            self.is_running = True
            self.voter_count = 0
            self.thread = threading.Thread(target=self.generate_voters_loop, daemon=True)
            self.thread.start()
            print("[VOTER GENERATOR] Started generating voters")
    
    def stop(self):
        """Stop the voter generator"""
        if self.is_running:
            self.is_running = False
            if self.thread:
                self.thread.join(timeout=5)
            print(f"[VOTER GENERATOR] Stopped. Total voters generated: {self.voter_count}")
    
    def get_realtime_votes(self):
        """Get real-time vote counts for current election"""
        try:
            conn = self.get_db_connection('users')
            election = conn.execute('SELECT * FROM elections WHERE status IN (?, ?) ORDER BY id DESC LIMIT 1',
                                   ('open', 'closed')).fetchone()
            conn.close()
            
            if not election:
                return {}
            
            conn = self.get_db_connection('votes')
            votes = conn.execute('''
                SELECT vote, COUNT(*) as count
                FROM votes
                WHERE election_id = ?
                GROUP BY vote
            ''', (election['id'],)).fetchall()
            conn.close()
            
            # Convert to dict
            vote_counts = {row['vote']: row['count'] for row in votes}
            
            # Ensure all parties are included (even with 0 votes)
            for party in PARTIES:
                if party not in vote_counts:
                    vote_counts[party] = 0
            
            return vote_counts
        except Exception as e:
            print(f"Error getting realtime votes: {e}")
            return {}
    
    def get_status(self):
        """Get current generator status"""
        return {
            'running': self.is_running,
            'voter_count': self.voter_count,
            'realtime_votes': self.get_realtime_votes()
        }
