-- City`s Social Support App Project

-- Table to store users: people who ask for help or volunteers who offer help
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each user
    full_name TEXT NOT NULL,                     -- User's full name
    email_address TEXT UNIQUE NOT NULL,          -- User's email (must be unique)
    phone_number TEXT,                           -- Optional phone number
    user_role TEXT CHECK (user_role IN ('help_requester', 'volunteer')) NOT NULL, -- Role: asker or helper
    is_verified BOOLEAN DEFAULT FALSE            -- If user is verified or not (default = no)
);

-- Table to store neighborhoods (local areas)
CREATE TABLE Neighborhoods (
    neighborhood_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each neighborhood
    neighborhood_name TEXT NOT NULL,                      -- Name of the neighborhood
    district_name TEXT,                                   -- Larger area or district name (optional)
    postal_code TEXT                                      -- Postal/zip code (optional)
);

-- Table for help requests made by users
CREATE TABLE HelpRequests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,        -- Unique ID for each request
    requester_id INTEGER NOT NULL,                        -- ID of the user asking for help
    neighborhood_id INTEGER NOT NULL,                     -- Neighborhood where help is needed
    help_category TEXT NOT NULL,                          -- Type of help needed (e.g., food, shelter)
    request_description TEXT,                             -- Extra details about the request (optional)
    urgency_level TEXT CHECK (urgency_level IN ('low', 'medium', 'high')) NOT NULL, -- How urgent it is
    request_status TEXT CHECK (request_status IN ('pending', 'fulfilled', 'expired')) DEFAULT 'pending', -- Status of request
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,        -- When the request was created
    FOREIGN KEY (requester_id) REFERENCES Users(user_id),  -- Link to Users table
    FOREIGN KEY (neighborhood_id) REFERENCES Neighborhoods(neighborhood_id) -- Link to Neighborhoods table
);

-- Table to store community resources available to help
CREATE TABLE CommunityResources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,       -- Unique ID for each resource
    organization_name TEXT NOT NULL,                      -- Name of the organization providing resource
    resource_type TEXT NOT NULL,                          -- Type of resource (e.g., food, medical)
    resource_location TEXT NOT NULL,                      -- Location of the resource
    neighborhood_id INTEGER NOT NULL,                      -- Neighborhood where resource is available
    available_capacity INTEGER CHECK (available_capacity >= 0), -- How much resource is available
    FOREIGN KEY (neighborhood_id) REFERENCES Neighborhoods(neighborhood_id)
);

-- Table to record which volunteer fulfilled which request
CREATE TABLE RequestFulfillments (
    fulfillment_id INTEGER PRIMARY KEY AUTOINCREMENT,    -- Unique ID for each fulfillment record
    request_id INTEGER NOT NULL,                          -- ID of the help request fulfilled
    volunteer_id INTEGER NOT NULL,                         -- ID of the volunteer who helped
    fulfilled_at DATETIME DEFAULT CURRENT_TIMESTAMP,      -- When it was fulfilled
    volunteer_feedback TEXT,                              -- Feedback from volunteer (optional)
    FOREIGN KEY (request_id) REFERENCES HelpRequests(request_id),
    FOREIGN KEY (volunteer_id) REFERENCES Users(user_id)
);

-- Simple indexes to help speed up searches (optional for beginners)
CREATE INDEX idx_help_requests_requester ON HelpRequests(requester_id);
CREATE INDEX idx_help_requests_neighborhood ON HelpRequests(neighborhood_id);
CREATE INDEX idx_help_requests_category ON HelpRequests(help_category);

CREATE INDEX idx_resources_neighborhood ON CommunityResources(neighborhood_id);

CREATE INDEX idx_fulfillments_request ON RequestFulfillments(request_id);
CREATE INDEX idx_fulfillments_volunteer ON RequestFulfillments(volunteer_id);

-- View: Shows active (pending) help requests with info about the requester and volunteers nearby
CREATE VIEW Active_Help_Requests_With_Volunteers AS
SELECT
    hr.request_id,
    hr.help_category,
    hr.request_description,
    hr.urgency_level,
    hr.created_at AS request_time,
    req.full_name AS requester_name,
    req.phone_number AS requester_phone,
    n.neighborhood_name,
    n.district_name,
    vol.user_id AS volunteer_id,
    vol.full_name AS volunteer_name,
    vol.phone_number AS volunteer_phone
FROM HelpRequests hr
JOIN Users req ON hr.requester_id = req.user_id
JOIN Neighborhoods n ON hr.neighborhood_id = n.neighborhood_id
LEFT JOIN Users vol ON vol.user_role = 'volunteer' AND vol.is_verified = TRUE
    AND vol.user_id IN (
        SELECT user_id FROM Users WHERE user_role = 'volunteer'
    )
WHERE hr.request_status = 'pending'
ORDER BY hr.urgency_level DESC, hr.created_at ASC;

-- View: Summary of resources and requests per neighborhood
CREATE VIEW Neighborhood_Help_Resource_Summary AS
SELECT
    n.neighborhood_id,
    n.neighborhood_name,
    n.district_name,
    n.postal_code,
    COUNT(DISTINCT cr.resource_id) AS total_resources,
    COUNT(DISTINCT CASE WHEN cr.resource_type = 'food' THEN cr.resource_id END) AS food_resources,
    COUNT(DISTINCT CASE WHEN cr.resource_type = 'shelter' THEN cr.resource_id END) AS shelter_resources,
    COUNT(DISTINCT CASE WHEN cr.resource_type = 'medical' THEN cr.resource_id END) AS medical_resources,
    COUNT(DISTINCT hr.request_id) AS total_requests,
    COUNT(DISTINCT CASE WHEN hr.request_status = 'pending' THEN hr.request_id END) AS pending_requests,
    COUNT(DISTINCT CASE WHEN hr.request_status = 'fulfilled' THEN hr.request_id END) AS fulfilled_requests,
    COUNT(DISTINCT CASE WHEN hr.urgency_level = 'high' THEN hr.request_id END) AS high_urgency_requests,
    COUNT(DISTINCT rf.fulfillment_id) AS total_fulfillments
FROM Neighborhoods n
LEFT JOIN CommunityResources cr ON n.neighborhood_id = cr.neighborhood_id
LEFT JOIN HelpRequests hr ON n.neighborhood_id = hr.neighborhood_id
LEFT JOIN RequestFulfillments rf ON hr.request_id = rf.request_id
GROUP BY n.neighborhood_id, n.neighborhood_name, n.district_name, n.postal_code
ORDER BY n.district_name, n.neighborhood_name;
