-- Queries for Requesters (people asking for help)

-- See my open (pending) help requests
SELECT
    request_id,
    help_category,
    request_description,
    urgency_level,
    request_status,
    created_at
FROM HelpRequests
WHERE requester_id = [CURRENT_USER_ID]   -- Replace with your user ID
  AND request_status = 'pending'          -- Only requests not yet fulfilled
ORDER BY urgency_level DESC, created_at ASC;

/* Purpose: Lets you track your active help requests,
   showing the most urgent ones first. */

-- Find resources available in my neighborhood
SELECT
    cr.resource_type,
    cr.organization_name,
    cr.resource_location,
    cr.available_capacity
FROM CommunityResources cr
JOIN Neighborhoods n ON cr.neighborhood_id = n.neighborhood_id
JOIN Users u ON n.neighborhood_id = (
    SELECT neighborhood_id
    FROM HelpRequests
    WHERE requester_id = u.user_id
    LIMIT 1
)
WHERE u.user_id = [CURRENT_USER_ID]       -- Your user ID here
  AND cr.available_capacity > 0            -- Only resources that have capacity
ORDER BY cr.resource_type;

/* Purpose: Helps you find nearby community resources
   without needing to submit a formal request. */

-- Update details of one of my requests
UPDATE HelpRequests
SET
    help_category = 'medical',
    request_description = 'Updated: Need insulin delivery',
    urgency_level = 'high'
WHERE request_id = [REQUEST_ID]           -- The request you want to update
  AND requester_id = [CURRENT_USER_ID]    -- Only if it's your request

/* Purpose: Lets you change your help request
   when your needs change. */

-- Queries for Volunteers (people helping others)

-- Find urgent help requests in my neighborhood
SELECT
    hr.request_id,
    hr.help_category,
    hr.request_description,
    hr.urgency_level,
    hr.created_at,
    n.neighborhood_name,
    u.full_name AS requester_name
FROM HelpRequests hr
JOIN Neighborhoods n ON hr.neighborhood_id = n.neighborhood_id
JOIN Users u ON hr.requester_id = u.user_id
WHERE hr.neighborhood_id IN (
    SELECT neighborhood_id
    FROM HelpRequests
    WHERE requester_id = [CURRENT_USER_ID]  -- Your user ID here
)
  AND hr.request_status = 'pending'         -- Only open requests
  AND u.is_verified = TRUE                   -- Only requests from verified users
ORDER BY hr.urgency_level DESC, hr.created_at ASC
LIMIT 10;

/* Purpose: Shows volunteers the top urgent requests nearby
   that they can help with. */

-- Mark a request as fulfilled (completed)
INSERT INTO RequestFulfillments (
    request_id,
    volunteer_id,
    volunteer_feedback
) VALUES (
    [REQUEST_ID],          -- Request you fulfilled
    [CURRENT_USER_ID],     -- Your user ID
    'Delivered groceries successfully' -- Optional feedback
);

UPDATE HelpRequests
SET request_status = 'fulfilled'
WHERE request_id = [REQUEST_ID];

/* Purpose: Records that you helped with a request
   and updates its status. */

-- View my volunteer history
SELECT
    hr.help_category,
    hr.request_description,
    rf.fulfilled_at,
    rf.volunteer_feedback,
    u.full_name AS helped_requester
FROM RequestFulfillments rf
JOIN HelpRequests hr ON rf.request_id = hr.request_id
JOIN Users u ON hr.requester_id = u.user_id
WHERE rf.volunteer_id = [CURRENT_USER_ID]    -- Your user ID
ORDER BY rf.fulfilled_at DESC;

/* Purpose: Lets volunteers see all the help they’ve given
   and feedback they received. */
3. Queries for All Users (requesters and volunteers)

-- Update my profile information
UPDATE Users
SET
    full_name = 'New Name',
    phone_number = '555-9876',
    email_address = 'newemail@example.com'
WHERE user_id = [CURRENT_USER_ID];

/* Purpose: Keeps your contact info up to date. */

-- See summary of neighborhood help needs and resources
SELECT
    neighborhood_name,
    district_name,
    (SELECT COUNT(*) FROM HelpRequests hr
     WHERE hr.neighborhood_id = n.neighborhood_id
       AND hr.request_status = 'pending') AS active_requests,
    (SELECT COUNT(*) FROM CommunityResources cr
     WHERE cr.neighborhood_id = n.neighborhood_id) AS available_resources
FROM Neighborhoods n
WHERE n.neighborhood_id IN (
    SELECT neighborhood_id
    FROM HelpRequests
    WHERE requester_id = [CURRENT_USER_ID]
)
ORDER BY active_requests DESC;

/* Purpose: Lets you understand how busy your neighborhood is
   and what help resources are available. */

-- Search for help requests by category (e.g., food)
SELECT
    hr.request_id,
    hr.help_category,
    hr.request_description,
    n.neighborhood_name,
    hr.created_at
FROM HelpRequests hr
JOIN Neighborhoods n ON hr.neighborhood_id = n.neighborhood_id
WHERE hr.help_category LIKE '%food%'
  AND hr.request_status = 'pending'
  AND n.neighborhood_id IN (
    SELECT neighborhood_id
    FROM HelpRequests
    WHERE requester_id = [CURRENT_USER_ID]
)
ORDER BY hr.urgency_level DESC;

/* Purpose: Helps you find requests needing specific types of help,
   like food or medical assistance. */
