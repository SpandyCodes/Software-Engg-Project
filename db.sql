CREATE TABLE IF NOT EXISTS User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    email VARCHAR(255),
    photo BLOB,
    passwrd VARCHAR(255),
    confirm_passwrd VARCHAR(255),
    DOB DATE,
    skills VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Grp (
    group_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    admin INT,
    FOREIGN KEY (admin) REFERENCES User(user_id),
    creation_date DATE
);

CREATE TABLE IF NOT EXISTS GroupMember (
    grpmember_id INT PRIMARY KEY AUTO_INCREMENT,
    grp_id INT,
    user_id INT,
    role VARCHAR(255),
    FOREIGN KEY (grp_id) REFERENCES Grp(group_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE IF NOT EXISTS Task (
    task_id INT PRIMARY KEY AUTO_INCREMENT,
    task_name VARCHAR(1000),
    deadline DATE,
    assigned_to INT,
    FOREIGN KEY (assigned_to) REFERENCES User(user_id),
    status VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender INT,
    time DATETIME DEFAULT CURRENT_TIMESTAMP,
    feedback_content TEXT,
    FOREIGN KEY (sender) REFERENCES User(user_id)
);

CREATE TABLE IF NOT EXISTS Messages (
    msg_id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT,
    group_id INT,
    date DATETIME,
    time TIME,
    msg_content TEXT,
    FOREIGN KEY (sender_id) REFERENCES User(user_id),
    FOREIGN KEY (group_id) REFERENCES Grp(group_id)
);

CREATE TABLE IF NOT EXISTS Announcements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    grp_id INT,
    user_id INT,
    content TEXT,
    date DATETIME,
    FOREIGN KEY (grp_id) REFERENCES Grp(group_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);


ALTER TABLE grp MODIFY COLUMN admin VARCHAR(100);
