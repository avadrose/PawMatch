# PawMatch Database Relationships


- `||` = exactly one
- `o|` = zero or one
- `o{` = zero or many

    USER o|--o{ DOG : owns
    SHELTER o|--o{ DOG : lists

    USER ||--o{ FAVORITE : creates
    DOG ||--o{ FAVORITE : receives

    USER ||--o{ ADOPTION_REQUEST : submits
    DOG ||--o{ ADOPTION_REQUEST : receives

    DOG ||--o{ PLAYDATE_REQUEST : "requests playdate as requester"
    DOG ||--o{ PLAYDATE_REQUEST : "receives playdate as recipient"

    USER ||--o{ MESSAGE : sends
    USER ||--o{ MESSAGE : receives

    USER ||--o{ REVIEW : writes
    USER ||--o{ REVIEW : receives
    PLAYDATE_REQUEST ||--o{ REVIEW : relates_to