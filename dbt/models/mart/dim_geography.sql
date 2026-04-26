WITH states AS (
    SELECT DISTINCT state AS state_abbrev
    FROM {{ ref('stg_complaints') }}
    WHERE state IS NOT NULL
),

state_lookup (state_abbrev, state_name, region) AS (
    SELECT * FROM (VALUES
        ('AL','Alabama','South'),('AK','Alaska','West'),('AZ','Arizona','West'),
        ('AR','Arkansas','South'),('CA','California','West'),('CO','Colorado','West'),
        ('CT','Connecticut','Northeast'),('DE','Delaware','Northeast'),
        ('DC','District of Columbia','South'),('FL','Florida','South'),
        ('GA','Georgia','South'),('HI','Hawaii','West'),('ID','Idaho','West'),
        ('IL','Illinois','Midwest'),('IN','Indiana','Midwest'),('IA','Iowa','Midwest'),
        ('KS','Kansas','Midwest'),('KY','Kentucky','South'),('LA','Louisiana','South'),
        ('ME','Maine','Northeast'),('MD','Maryland','Northeast'),
        ('MA','Massachusetts','Northeast'),('MI','Michigan','Midwest'),
        ('MN','Minnesota','Midwest'),('MS','Mississippi','South'),
        ('MO','Missouri','Midwest'),('MT','Montana','West'),('NE','Nebraska','Midwest'),
        ('NV','Nevada','West'),('NH','New Hampshire','Northeast'),('NJ','New Jersey','Northeast'),
        ('NM','New Mexico','West'),('NY','New York','Northeast'),
        ('NC','North Carolina','South'),('ND','North Dakota','Midwest'),
        ('OH','Ohio','Midwest'),('OK','Oklahoma','South'),('OR','Oregon','West'),
        ('PA','Pennsylvania','Northeast'),('PR','Puerto Rico','South'),
        ('RI','Rhode Island','Northeast'),('SC','South Carolina','South'),
        ('SD','South Dakota','Midwest'),('TN','Tennessee','South'),
        ('TX','Texas','South'),('UT','Utah','West'),('VT','Vermont','Northeast'),
        ('VA','Virginia','South'),('WA','Washington','West'),
        ('WV','West Virginia','South'),('WI','Wisconsin','Midwest'),
        ('WY','Wyoming','West'),('AA','Armed Forces Americas','Other'),
        ('AE','Armed Forces Europe','Other'),('AP','Armed Forces Pacific','Other')
    )
)

SELECT
    ROW_NUMBER() OVER (ORDER BY s.state_abbrev) AS state_key,
    s.state_abbrev,
    COALESCE(l.state_name, s.state_abbrev)      AS state_name,
    COALESCE(l.region, 'Other')                 AS region
FROM states s
LEFT JOIN state_lookup l ON s.state_abbrev = l.state_abbrev
