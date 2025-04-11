CREATE TABLE doctors (
    id INTEGER PRIMARY KEY, -- Changed to INTEGER PRIMARY KEY for auto-increment in SQLite
    doctor_name VARCHAR(255),
    specialization VARCHAR(100),
    field_of_interest VARCHAR(255),
    institution_id INTEGER -- Changed to INTEGER to match the institutions.id type
);

CREATE TABLE institutions (
    id INTEGER PRIMARY KEY, -- Changed to INTEGER PRIMARY KEY for auto-increment in SQLite
    institution_name VARCHAR(255),
    institution_type VARCHAR(20),
    institution_address VARCHAR(255),
    CONSTRAINT institutions_institution_type_check CHECK (institution_type IN ('Private', 'Public')) -- Simplified the CHECK constraint
);

INSERT INTO institutions (id, institution_name, institution_type, institution_address) VALUES
    (1, 'Mayo Clinic', 'Private', '200 1st St SW, Rochester, MN'),
    (2, 'Cleveland Clinic', 'Private', '9500 Euclid Ave, Cleveland, OH'),
    (3, 'Johns Hopkins Hospital', 'Public', '1800 Orleans St, Baltimore, MD'),
    (4, 'Massachusetts General Hospital', 'Public', '55 Fruit St, Boston, MA'),
    (5, 'UCLA Medical Center', 'Public', '757 Westwood Plaza, Los Angeles, CA'),
    (6, 'NewYork-Presbyterian Hospital', 'Public', '525 E 68th St, New York, NY'),
    (7, 'Cedars-Sinai Medical Center', 'Private', '8700 Beverly Blvd, Los Angeles, CA'),
    (8, 'Stanford Health Care', 'Private', '300 Pasteur Dr, Stanford, CA'),
    (9, 'Mount Sinai Hospital', 'Public', '1468 Madison Ave, New York, NY'),
    (10, 'Houston Methodist Hospital', 'Private', '6565 Fannin St, Houston, TX');

INSERT INTO doctors (id, doctor_name, specialization, field_of_interest, institution_id) VALUES
    (1, 'Olivia Miller', 'Internal Medicine', 'Stroke', 10),
    (2, 'Emma Rodriguez', 'Psychiatry', 'Childhood Asthma', 5),
    (3, 'James Brown', 'Ophthalmology', 'Hypertension', 5),
    (4, 'Sarah Smith', 'Pediatrics', 'Pregnancy', 1),
    (5, 'Michael Garcia', 'Dermatology', 'Stroke', 2),
    (6, 'James Rodriguez', 'Dermatology', 'Childhood Asthma', 6),
    (7, 'Emily Williams', 'Internal Medicine', 'Pregnancy', 5),
    (8, 'Olivia Smith', 'Cardiology', 'Pregnancy', 10),
    (9, 'John Miller', 'Orthopedics', 'Depression', 3),
    (10, 'Emma Davis', 'Neurology', 'Diabetes', 6);
INSERT INTO doctors (id, doctor_name, specialization, field_of_interest, institution_id) VALUES
    (11, 'Sophia Jones', 'Surgery', 'Cataracts', 7),
    (12, 'John Miller', 'Pediatrics', 'Cataracts', 5),
    (13, 'Olivia Garcia', 'Dermatology', 'Diabetes', 8),
    (14, 'Sarah Johnson', 'Internal Medicine', 'Appendicitis', 6),
    (15, 'James Johnson', 'Gynecology', 'Hypertension', 7),
    (16, 'Emily Williams', 'Neurology', 'Diabetes', 6),
    (17, 'James Smith', 'Gynecology', 'Acne', 8),
    (18, 'Michael Rodriguez', 'Ophthalmology', 'Childhood Asthma', 9),
    (19, 'Sophia Jones', 'Dermatology', 'Diabetes', 9),
    (20, 'John Williams', 'Ophthalmology', 'Stroke', 4);
INSERT INTO doctors (id, doctor_name, specialization, field_of_interest, institution_id) VALUES
    (21, 'Sophia Smith', 'Ophthalmology', 'Appendicitis', 7),
    (22, 'Michael Garcia', 'Orthopedics', 'Childhood Asthma', 7),
    (23, 'John Davis', 'Pediatrics', 'Bone Fractures', 9),
    (24, 'James Williams', 'Pediatrics', 'Stroke', 8),
    (25, 'Sarah Davis', 'Ophthalmology', 'Cataracts', 8),
    (26, 'Robert Brown', 'Psychiatry', 'Childhood Asthma', 3),
    (27, 'Michael Garcia', 'Surgery', 'Stroke', 1),
    (28, 'Sophia Miller', 'Neurology', 'Depression', 7),
    (29, 'John Martinez', 'Psychiatry', 'Childhood Asthma', 7),
    (30, 'Olivia Miller', 'Surgery', 'Stroke', 6);
INSERT INTO doctors (id, doctor_name, specialization, field_of_interest, institution_id) VALUES
    (31, 'Emily Johnson', 'Ophthalmology', 'Diabetes', 8),
    (32, 'Emma Martinez', 'Psychiatry', 'Pregnancy', 7),
    (33, 'James Garcia', 'Surgery', 'Hypertension', 4),
    (34, 'Olivia Garcia', 'Surgery', 'Bone Fractures', 9),
    (35, 'David Davis', 'Dermatology', 'Bone Fractures', 5),
    (36, 'Sarah Rodriguez', 'Orthopedics', 'Stroke', 7),
    (37, 'Olivia Brown', 'Gynecology', 'Childhood Asthma', 5),
    (38, 'Emily Davis', 'Psychiatry', 'Childhood Asthma', 9),
    (39, 'Emma Jones', 'Cardiology', 'Depression', 3),
    (40, 'James Martinez', 'Cardiology', 'Acne', 3);
INSERT INTO doctors (id, doctor_name, specialization, field_of_interest, institution_id) VALUES
    (41, 'John Brown', 'Ophthalmology', 'Appendicitis', 5),
    (42, 'Sarah Smith', 'Pediatrics', 'Diabetes', 4),
    (43, 'Olivia Jones', 'Dermatology', 'Childhood Asthma', 8),
    (44, 'James Miller', 'Surgery', 'Cataracts', 7),
    (45, 'Sophia Johnson', 'Pediatrics', 'Hypertension', 5),
    (46, 'Sophia Williams', 'Dermatology', 'Depression', 7),
    (47, 'Michael Miller', 'Ophthalmology', 'Hypertension', 2),
    (48, 'David Jones', 'Cardiology', 'Acne', 3),
    (49, 'James Martinez', 'Neurology', 'Childhood Asthma', 4),
    (50, 'James Miller', 'Psychiatry', 'Cataracts', 8);
INSERT INTO doctors (id, doctor_name, specialization, field_of_interest, institution_id) VALUES
    (51, 'Sophia Johnson', 'Surgery', 'Pregnancy', 3),
    (52, 'David Miller', 'Orthopedics', 'Bone Fractures', 10),
    (53, 'Olivia Martinez', 'Internal Medicine', 'Appendicitis', 5),
    (54, 'Michael Martinez', 'Gynecology', 'Bone Fractures', 5),
    (55, 'Michael Williams', 'Gynecology', 'Pregnancy', 7),
    (56, 'Michael Miller', 'Psychiatry', 'Cataracts', 10),
    (57, 'Olivia Brown', 'Ophthalmology', 'Depression', 7),
    (58, 'Michael Garcia', 'Ophthalmology', 'Childhood Asthma', 7),
    (59, 'Robert Davis', 'Dermatology', 'Depression', 10),
    (60, 'Michael Johnson', 'Surgery', 'Childhood Asthma', 4);
INSERT INTO doctors (id, doctor_name, specialization, field_of_interest, institution_id) VALUES
    (61, 'David Martinez', 'Cardiology', 'Acne', 2),
    (62, 'Michael Smith', 'Surgery', 'Childhood Asthma', 10),
    (63, 'Sophia Miller', 'Psychiatry', 'Acne', 9),
    (64, 'Emily Smith', 'Dermatology', 'Stroke', 1),
    (65, 'Emma Martinez', 'Ophthalmology', 'Hypertension', 7),
    (66, 'James Smith', 'Gynecology', 'Appendicitis', 1),
    (67, 'Emily Jones', 'Pediatrics', 'Cataracts', 10),
    (68, 'James Rodriguez', 'Ophthalmology', 'Childhood Asthma', 6),
    (69, 'Olivia Garcia', 'Pediatrics', 'Childhood Asthma', 10),
    (70, 'Michael Jones', 'Cardiology', 'Depression', 7);
INSERT INTO doctors (id, doctor_name, specialization, field_of_interest, institution_id) VALUES
    (71, 'Sarah Martinez', 'Dermatology', 'Stroke', 10),
    (72, 'Michael Williams', 'Cardiology', 'Childhood Asthma', 4),
    (73, 'Sarah Miller', 'Ophthalmology', 'Diabetes', 9),
    (74, 'Sophia Miller', 'Surgery', 'Acne', 10),
    (75, 'Sarah Smith', 'Pediatrics', 'Pregnancy', 8),
    (76, 'Emma Rodriguez', 'Dermatology', 'Appendicitis', 9),
    (77, 'Emily Williams', 'Surgery', 'Pregnancy', 8),
    (78, 'Sarah Brown', 'Psychiatry', 'Bone Fractures', 10),
    (79, 'James Williams', 'Ophthalmology', 'Diabetes', 4),
    (80, 'Emily Jones', 'Internal Medicine', 'Pregnancy', 5);
INSERT INTO doctors (id, doctor_name, specialization, field_of_interest, institution_id) VALUES
    (81, 'Sophia Martinez', 'Orthopedics', 'Pregnancy', 5),
    (82, 'Michael Jones', 'Neurology', 'Cataracts', 9),
    (83, 'Robert Williams', 'Gynecology', 'Hypertension', 7),
    (84, 'Sophia Brown', 'Neurology', 'Depression', 5),
    (85, 'Robert Miller', 'Pediatrics', 'Stroke', 1),
    (86, 'Olivia Garcia', 'Orthopedics', 'Acne', 10),
    (87, 'Emma Martinez', 'Ophthalmology', 'Hypertension', 4),
    (88, 'Emily Williams', 'Dermatology', 'Childhood Asthma', 10),
    (89, 'Sarah Williams', 'Internal Medicine', 'Depression', 9),
    (90, 'Olivia Miller', 'Surgery', 'Appendicitis', 10);
INSERT INTO doctors (id, doctor_name, specialization, field_of_interest, institution_id) VALUES
    (91, 'Sarah Martinez', 'Pediatrics', 'Childhood Asthma', 10),
    (92, 'Emma Davis', 'Surgery', 'Appendicitis', 1),
    (93, 'David Williams', 'Dermatology', 'Cataracts', 2),
    (94, 'James Jones', 'Psychiatry', 'Cataracts', 3),
    (95, 'Sophia Johnson', 'Surgery', 'Acne', 7),
    (96, 'Emily Brown', 'Ophthalmology', 'Bone Fractures', 6),
    (97, 'Robert Miller', 'Dermatology', 'Appendicitis', 9),
    (98, 'Robert Jones', 'Gynecology', 'Pregnancy', 2),
    (99, 'Sophia Smith', 'Neurology', 'Stroke', 7),
    (100, 'Robert Smith', 'Gynecology', 'Pregnancy', 4);