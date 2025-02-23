CREATE DATABASE FitnessCenter

CREATE TABLE Users (
    UserID INT IDENTITY(1,1) NOT NULL,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Parola VARCHAR(255) NOT NULL,
    Rol VARCHAR(10) NOT NULL CHECK (Rol IN ('client', 'admin')),
    Nume VARCHAR(100) NOT NULL,
    DataNasterii DATE,
    NumarTelefon VARCHAR(15),
    Email VARCHAR(100) NOT NULL UNIQUE,
    Adresa TEXT,
    CONSTRAINT PK_Users PRIMARY KEY (UserID)
);

CREATE TABLE Abonament (
    AbonamentID INT IDENTITY(1,1) NOT NULL,
    TipAbonament VARCHAR(10) NOT NULL CHECK (TipAbonament IN ('strength', 'cardio', 'full body')),
    Pret DECIMAL(10,2) NOT NULL,
    Valabilitate INT NOT NULL,
    CONSTRAINT PK_Abonament PRIMARY KEY (AbonamentID)
);

CREATE TABLE Echipamente (
    EchipamentID INT IDENTITY(1,1) NOT NULL,
    Denumire VARCHAR(100) NOT NULL,
    Tip VARCHAR(50) NOT NULL,
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('functional', 'under maintenance')),
    CONSTRAINT PK_Echipamente PRIMARY KEY (EchipamentID)
);

CREATE TABLE Antrenori (
    AntrenorID INT IDENTITY(1,1) NOT NULL,
    Nume VARCHAR(50) NOT NULL,
    Prenume VARCHAR(50) NOT NULL,
    Specializare VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    NumarTelefon VARCHAR(15),
    CONSTRAINT PK_Antrenori PRIMARY KEY (AntrenorID)
);

CREATE TABLE Clase (
    ClasaID INT IDENTITY(1,1) NOT NULL,
    Denumire VARCHAR(100) NOT NULL,
    Descriere TEXT,
    AntrenorID INT NOT NULL,
    Ora TIME NOT NULL,
    CONSTRAINT PK_Clase PRIMARY KEY (ClasaID),
    CONSTRAINT FK_Clase_Antrenori FOREIGN KEY (AntrenorID) REFERENCES Antrenori(AntrenorID) ON DELETE CASCADE
);

CREATE TABLE DetaliiClase (
    UserID INT NOT NULL,
    ClasaID INT NOT NULL,
    DataInscrierii DATE NOT NULL,
    CONSTRAINT PK_DetaliiClase PRIMARY KEY (UserID, ClasaID),
    CONSTRAINT FK_DetaliiClase_Users FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    CONSTRAINT FK_DetaliiClase_Clase FOREIGN KEY (ClasaID) REFERENCES Clase(ClasaID) ON DELETE CASCADE
);

CREATE TABLE UtilizareEchipamente (
    UserID INT NOT NULL,
    EchipamentID INT NOT NULL,
    DataUtilizarii DATE NOT NULL,
    OraInceput TIME NOT NULL,
    OraSfarsit TIME NOT NULL,
    CONSTRAINT PK_UtilizareEchipamente PRIMARY KEY (UserID, EchipamentID, DataUtilizarii),
    CONSTRAINT FK_UtilizareEchipamente_Users FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    CONSTRAINT FK_UtilizareEchipamente_Echipamente FOREIGN KEY (EchipamentID) REFERENCES Echipamente(EchipamentID) ON DELETE CASCADE
);

CREATE TABLE Feedback (
    FeedbackID INT IDENTITY(1,1) NOT NULL,
    UserID INT NOT NULL,
    Comentarii TEXT NOT NULL,
    DataFeedback DATE NOT NULL,
    CONSTRAINT PK_Feedback PRIMARY KEY (FeedbackID),
    CONSTRAINT FK_Feedback_Users FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);

CREATE TABLE UserDetails (
    DetailID INT IDENTITY(1,1) NOT NULL,
    UserID INT NOT NULL,
    Nume VARCHAR(100) NOT NULL,
    TipAbonament VARCHAR(50),
    PretAbonament DECIMAL(10, 2),
    ClasaID INT,
    DenumireClasa VARCHAR(100),
    DataInscrierii DATE,
    CONSTRAINT PK_UserDetails PRIMARY KEY (DetailID),
    CONSTRAINT FK_UserDetails_Users FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    CONSTRAINT FK_UserDetails_Clase FOREIGN KEY (ClasaID) REFERENCES Clase(ClasaID) ON DELETE CASCADE
);


INSERT INTO UserDetails (UserID, Nume, TipAbonament, PretAbonament, DenumireClasa, DataInscrierii)
SELECT 
    u.UserID,
    u.Nume,
    a.TipAbonament,
    a.Pret,
    c.Denumire AS DenumireClasa,
    dc.DataInscrierii
FROM Users u
LEFT JOIN Abonament a ON u.UserID = a.AbonamentID
LEFT JOIN DetaliiClase dc ON u.UserID = dc.UserID
LEFT JOIN Clase c ON dc.ClasaID = c.ClasaID;

-- Populare tabel Users
INSERT INTO Users (Username, Parola, Rol, Nume, DataNasterii, NumarTelefon, Email, Adresa)
VALUES 
    ('john_doe', 'password123', 'client', 'John Doe', '1990-05-15', '0721123456', 'john.doe@example.com', '123 Main St'),
    ('jane_doe', 'securepass', 'client', 'Jane Doe', '1992-08-25', '0721345678', 'jane.doe@example.com', '456 Elm St'),
    ('admin1', 'adminpass', 'admin', 'Admin One', NULL, NULL, 'admin1@fitnesscenter.com', NULL),
    ('mark_smith', 'mypassword', 'client', 'Mark Smith', '1985-03-10', '0732123456', 'mark.smith@example.com', '789 Oak St'),
    ('lisa_jones', 'lisapass', 'client', 'Lisa Jones', '1988-07-20', '0743123456', 'lisa.jones@example.com', '321 Pine St');


INSERT INTO Users (Username, Parola, Rol, Nume, DataNasterii, NumarTelefon, Email, Adresa)
VALUES 
    ('andrei_popescu', 'andrei123', 'client', 'Andrei Popescu', '1995-11-20', '0722345678', 'andrei.popescu@example.com', '1000 Liberty St'),
    ('catalina_marin', 'catalina456', 'client', 'Catalina Marin', '1993-04-18', '0733456789', 'catalina.marin@example.com', '2000 Oak Avenue');


-- Populare tabel Abonament
INSERT INTO Abonament (TipAbonament, Pret, Valabilitate)
VALUES 
    ('strength', 100.00, 30),
    ('cardio', 80.00, 30),
    ('full body', 150.00, 30),
    ('strength', 250.00, 90),
    ('cardio', 200.00, 90);

-- Populare tabel Echipamente
INSERT INTO Echipamente (Denumire, Tip, Status)
VALUES 
    ('Treadmill', 'Cardio', 'functional'),
    ('Dumbbells', 'Strength', 'functional'),
    ('Stationary Bike', 'Cardio', 'under maintenance'),
    ('Barbell', 'Strength', 'functional'),
    ('Rowing Machine', 'Cardio', 'functional');

-- Populare tabel Antrenori
INSERT INTO Antrenori (Nume, Prenume, Specializare, Email, NumarTelefon)
VALUES 
    ('Alex', 'Popescu', 'Fitness', 'alex.popescu@fitnesscenter.com', '0755123456'),
    ('Maria', 'Ionescu', 'Aerobic', 'maria.ionescu@fitnesscenter.com', '0756123456'),
    ('Cristian', 'Vasilescu', 'Yoga', 'cristian.vasilescu@fitnesscenter.com', '0757123456'),
    ('Elena', 'Radu', 'Pilates', 'elena.radu@fitnesscenter.com', '0758123456'),
    ('George', 'Toma', 'Cardio', 'george.toma@fitnesscenter.com', '0759123456');

-- Populare tabel Clase
INSERT INTO Clase (Denumire, Descriere, AntrenorID, Ora)
VALUES 
    ('Yoga Class', 'A relaxing yoga session.', 3, '09:00:00'),
    ('Aerobic Class', 'High energy aerobic exercises.', 2, '10:30:00'),
    ('Pilates Class', 'Improve core strength and posture.', 4, '14:00:00'),
    ('Cardio Class', 'Intensive cardio training.', 5, '16:00:00'),
    ('Strength Training', 'Build muscle and strength.', 1, '18:00:00');

-- Populare tabel DetaliiClase
INSERT INTO DetaliiClase (UserID, ClasaID, DataInscrierii)
VALUES 
    (1, 1, '2024-11-10'),
    (2, 2, '2024-11-11'),
    (4, 3, '2024-11-12'),
    (5, 4, '2024-11-13'),
    (1, 5, '2024-11-14');

-- Populare tabel UtilizareEchipamente
INSERT INTO UtilizareEchipamente (UserID, EchipamentID, DataUtilizarii, OraInceput, OraSfarsit)
VALUES 
    (1, 1, '2024-11-15', '09:00:00', '09:30:00'),
    (2, 2, '2024-11-15', '10:00:00', '10:45:00'),
    (4, 3, '2024-11-15', '11:00:00', '11:20:00'),
    (5, 4, '2024-11-15', '12:00:00', '12:50:00'),
    (1, 5, '2024-11-15', '13:00:00', '13:30:00');

-- Populare tabel Feedback
INSERT INTO Feedback (UserID, Comentarii, DataFeedback)
VALUES 
    (1, 'Great equipment and facilities.', '2024-11-15'),
    (2, 'Friendly staff and good classes.', '2024-11-15'),
    (4, 'Yoga class was amazing.', '2024-11-15'),
    (5, 'Would love more cardio equipment.', '2024-11-15'),
    (1, 'Strength training was excellent.', '2024-11-15');


-- Verifică tabela Users
SELECT * FROM Users;

-- Verifică tabela Abonament
SELECT * FROM Abonament;

-- Verifică tabela Echipamente
SELECT * FROM Echipamente;

-- Verifică tabela Antrenori
SELECT * FROM Antrenori;

-- Verifică tabela Clase
SELECT * FROM Clase;

-- Verifică tabela DetaliiClase
SELECT * FROM DetaliiClase;

-- Verifică tabela UtilizareEchipamente
SELECT * FROM UtilizareEchipamente;

-- Verifică tabela Feedback
SELECT * FROM Feedback;

EXEC sp_columns Users;


SELECT 
    UserID,
    Nume,
    TipAbonament,
    PretAbonament,
    DenumireClasa,
    DataInscrierii
FROM UserDetails
ORDER BY UserID, DataInscrierii;

CREATE TRIGGER trg_InsertUserDetailsAbonament
ON Abonament
AFTER INSERT
AS
BEGIN
    -- Adaugă detaliile abonamentului în UserDetails
    INSERT INTO UserDetails (UserID, Nume, TipAbonament, PretAbonament)
    SELECT 
        u.UserID,
        u.Nume,
        i.TipAbonament,
        i.Pret
    FROM 
        Users u
    CROSS JOIN INSERTED i;
END;

CREATE TRIGGER trg_DeleteUserDetailsAbonament
ON Abonament
AFTER DELETE
AS
BEGIN
    -- Șterge detaliile abonamentului din UserDetails
    DELETE FROM UserDetails
    WHERE TipAbonament IN (
        SELECT d.TipAbonament
        FROM DELETED d
    );
END;


SELECT * FROM UserDetails;

EXEC sp_columns UserDetails;

SELECT DenumireClasa, Ora, CONCAT(a.Nume, ' ', a.Prenume) AS Trainer
FROM UserDetails ud
JOIN Clase c ON ud.ClasaID = c.ClasaID
JOIN Antrenori a ON c.AntrenorID = a.AntrenorID
WHERE ud.UserID = 1;



SELECT c.ClasaID, c.Denumire, c.Ora, CONCAT(a.Nume, ' ', a.Prenume) AS Trainer
FROM Clase c
JOIN Antrenori a ON c.AntrenorID = a.AntrenorID
WHERE c.ClasaID NOT IN (
    SELECT ClasaID FROM UserDetails WHERE UserID = 1
);

IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'trg_UpdateUserDetailsClasses')
    DROP TRIGGER trg_UpdateUserDetailsClasses;

GO
CREATE TRIGGER trg_UpdateUserDetailsClasses
ON DetaliiClase
AFTER INSERT, DELETE
AS
BEGIN
    -- Adăugăm doar clasele noi în UserDetails
    INSERT INTO UserDetails (UserID, Nume, ClasaID, DenumireClasa, DataInscrierii)
    SELECT 
        i.UserID,
        u.Nume,
        i.ClasaID,
        c.Denumire AS DenumireClasa,
        i.DataInscrierii
    FROM 
        INSERTED i
        JOIN Users u ON i.UserID = u.UserID
        JOIN Clase c ON i.ClasaID = c.ClasaID
    WHERE 
        NOT EXISTS (
            SELECT 1 
            FROM UserDetails ud 
            WHERE ud.UserID = i.UserID AND ud.ClasaID = i.ClasaID
        );

    -- Ștergem clasele din UserDetails dacă sunt eliminate din DetaliiClase
    DELETE FROM UserDetails
    WHERE ClasaID IS NOT NULL
    AND EXISTS (
        SELECT 1 
        FROM DELETED d
        WHERE UserDetails.UserID = d.UserID AND UserDetails.ClasaID = d.ClasaID
    );
END;

SELECT * FROM UserDetails;
