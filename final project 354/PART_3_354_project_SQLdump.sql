
DROP DATABASE IF EXISTS `proj_database`;
CREATE DATABASE `proj_database`;
USE `proj_database`;

-------------------------------------------------------------------------------
DELIMITER $$
CREATE TRIGGER AGE_CONSTRAINT
AFTER INSERT 
ON PERSON
FOR EACH ROW
BEGIN
IF NEW.age < 18 THEN  
	DELETE 
	FROM Person 
	WHERE username = NEW.username;
END IF;
END;

CREATE TRIGGER WEIGHT_CONSTRAINT
AFTER INSERT 
ON PERSON
FOR EACH ROW
BEGIN
IF NEW.weight <= 0 THEN  
	DELETE 
	FROM Person 
	WHERE username = NEW.username;
END IF;
END;

CREATE TRIGGER HEIGHT_CONSTRAINT
AFTER INSERT 
ON PERSON
FOR EACH ROW
BEGIN
IF NEW.height <= 0 THEN  
	DELETE 
	FROM Person 
	WHERE username = NEW.username;
END IF;
END;
DELIMITER ;



CREATE TABLE IF NOT EXISTS `Exercise` (
	`exercise_name` varchar(100) NOT NULL,
 	`functionality` varchar(100) NOT NULL,
 	PRIMARY KEY (`exercise_name`)
);

INSERT INTO `Exercise` VALUES('squat', 'functional');
INSERT INTO `Exercise` VALUES('benchpress', 'non-functional');
INSERT INTO `Exercise` VALUES('situps', 'functional');
INSERT INTO `Exercise` VALUES('shoulderpress', 'functional');
INSERT INTO `Exercise` VALUES('curl', 'non-functional');

INSERT INTO `Exercise` VALUES('wide grip pull-down', 'non-functional');
INSERT INTO `Exercise` VALUES('deadlift', 'non-functional');
INSERT INTO `Exercise` VALUES('squat jumps', 'non-functional');
INSERT INTO `Exercise` VALUES('burpees', 'non-functional');
INSERT INTO `Exercise` VALUES('hammer curls', 'non-functional');
INSERT INTO `Exercise` VALUES('push ups', 'functional');

-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `ExerciseTargetMuscle` (
	`exercise_name` varchar(100) NOT NULL,
 	`target_muscle` varchar(100) NOT NULL,
  CONSTRAINT `PK_ExerciseTargetMuscle` PRIMARY KEY (`exercise_name`, `target_muscle`),
  FOREIGN KEY (`exercise_name`) REFERENCES Exercise (`exercise_name`)
);

INSERT INTO `ExerciseTargetMuscle` VALUES('squat', 'quads');
INSERT INTO `ExerciseTargetMuscle` VALUES('benchpress', 'pectorials');
INSERT INTO `ExerciseTargetMuscle` VALUES('situps', 'heart');
INSERT INTO `ExerciseTargetMuscle` VALUES('shoulderpress', 'deltoids');
INSERT INTO `ExerciseTargetMuscle` VALUES('curl', 'biceps');
-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `ExerciseMuscleComponent` (
	`exercise_name` varchar(100) NOT NULL,
 	`muscle_component` varchar(100) NOT NULL,
 	CONSTRAINT `PK_ExerciseMuscleComponent` PRIMARY KEY (`exercise_name`, `muscle_component`),
  FOREIGN KEY (`exercise_name`) REFERENCES Exercise (`exercise_name`)
);

INSERT INTO `ExerciseMuscleComponent` VALUES('squat', 'legs');
INSERT INTO `ExerciseMuscleComponent` VALUES('benchpress', 'chest');
INSERT INTO `ExerciseMuscleComponent` VALUES('situps', 'full body');
INSERT INTO `ExerciseMuscleComponent` VALUES('shoulderpress', 'shoulders');
INSERT INTO `ExerciseMuscleComponent` VALUES('curl', 'arms');
-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Program` (
	`program_name` varchar(100) NOT NULL,
 	`intensity` varchar(100) NOT NULL,
  `duration` smallint UNSIGNED NOT NULL,
 	PRIMARY KEY (`program_name`)
);

INSERT INTO `Program` VALUES('strength training', 'low', 6);
INSERT INTO `Program` VALUES('conditioning', 'high', 8);
INSERT INTO `Program` VALUES('bodybuilding', 'med', 8);
INSERT INTO `Program` VALUES('crossfit', 'high', 10);
INSERT INTO `Program` VALUES('beginner', 'med', 6);
-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Contains` (
	`program_name` varchar(100) NOT NULL,
 	`exercise_name` varchar(100) NOT NULL,
    `sets` smallint UNSIGNED NOT NULL,
    `repetitions` smallint UNSIGNED NOT NULL,
 	CONSTRAINT `PK_Contains` PRIMARY KEY (`program_name`, `exercise_name`),
  FOREIGN KEY (`program_name`) REFERENCES Program (`program_name`),
  FOREIGN KEY (`exercise_name`) REFERENCES Exercise (`exercise_name`)
);

INSERT INTO `Contains` VALUES('bodybuilding', 'benchpress', 5, 10);
INSERT INTO `Contains` VALUES('bodybuilding', 'wide grip pull-down', 3, 12);
INSERT INTO `Contains` VALUES('bodybuilding', 'deadlift', 3, 12);
INSERT INTO `Contains` VALUES('conditioning', 'situps', 3, 20);
INSERT INTO `Contains` VALUES('conditioning', 'squat jumps', 3, 15);
INSERT INTO `Contains` VALUES('conditioning', 'burpees', 3, 10);
INSERT INTO `Contains` VALUES('strength training', 'squat', 5, 5);
INSERT INTO `Contains` VALUES('strength training', 'hammer curls', 3, 15);
INSERT INTO `Contains` VALUES('crossfit', 'shoulderpress', 3, 10);
INSERT INTO `Contains` VALUES('crossfit', 'burpees', 3, 10);
INSERT INTO `Contains` VALUES('crossfit', 'squat', 5, 15);
INSERT INTO `Contains` VALUES('beginner', 'curl', 3, 10);
INSERT INTO `Contains` VALUES('beginner', 'squat', 5, 5);
INSERT INTO `Contains` VALUES('beginner', 'push ups', 5, 10);

-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Meal` (
	`meal_name` varchar(100) NOT NULL,
 	`calories` smallint UNSIGNED NOT NULL,
 	PRIMARY KEY (`meal_name`)
);

INSERT INTO `Meal` VALUES('ham sandwich', 400);
INSERT INTO `Meal` VALUES('steamed salmon', 350);
INSERT INTO `Meal` VALUES('grilled chicken', 600);
INSERT INTO `Meal` VALUES('fish sandwich', 420);
INSERT INTO `Meal` VALUES('salad', 200);
INSERT INTO `Meal` VALUES('porkchops', 700);
INSERT INTO `Meal` VALUES('veggie burger', 400);
INSERT INTO `Meal` VALUES('carrots', 100);
INSERT INTO `Meal` VALUES('broccoli', 80);
INSERT INTO `Meal` VALUES('brussel sprouts', 110);
INSERT INTO `Meal` VALUES('cabbage', 95);
INSERT INTO `Meal` VALUES('asparagus', 105);
INSERT INTO `Meal` VALUES('eggplant', 100);
INSERT INTO `Meal` VALUES('cod', 400);
INSERT INTO `Meal` VALUES('sardine', 350);
INSERT INTO `Meal` VALUES('tuna', 450);

-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Veggie` (
	`meal_name` varchar(100) NOT NULL,
 	PRIMARY KEY (`meal_name`),
  FOREIGN KEY (`meal_name`) REFERENCES Meal (`meal_name`)
);

INSERT INTO `Veggie` VALUES('salad');
INSERT INTO `Veggie` VALUES('veggie burger');
INSERT INTO `Veggie` VALUES('carrots');
INSERT INTO `Veggie` VALUES('broccoli');
INSERT INTO `Veggie` VALUES('brussel sprouts');
INSERT INTO `Veggie` VALUES('cabbage');
INSERT INTO `Veggie` VALUES('asparagus');
INSERT INTO `Veggie` VALUES('eggplant');
-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Pescatarian` (
	`meal_name` varchar(100) NOT NULL,
 	PRIMARY KEY (`meal_name`),
  FOREIGN KEY (`meal_name`) REFERENCES Meal (`meal_name`)
);

INSERT INTO `Pescatarian` VALUES('salad');
INSERT INTO `Pescatarian` VALUES('steamed salmon');
INSERT INTO `Pescatarian` VALUES('fish sandwich');
INSERT INTO `Pescatarian` VALUES('broccoli');
INSERT INTO `Pescatarian` VALUES('carrots');
INSERT INTO `Pescatarian` VALUES('cod');
INSERT INTO `Pescatarian` VALUES('sardine');
INSERT INTO `Pescatarian` VALUES('tuna');
-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Omnivore` (
	`meal_name` varchar(100) NOT NULL,
 	PRIMARY KEY (`meal_name`),
  FOREIGN KEY (`meal_name`) REFERENCES Meal (`meal_name`)
);

INSERT INTO `Omnivore` VALUES('grilled chicken');
INSERT INTO `Omnivore` VALUES('ham sandwich');
INSERT INTO `Omnivore` VALUES('porkchops');
INSERT INTO `Omnivore` VALUES('salad');
INSERT INTO `Omnivore` VALUES('steamed salmon');
INSERT INTO `Omnivore` VALUES('tuna');
INSERT INTO `Omnivore` VALUES('cabbage');
INSERT INTO `Omnivore` VALUES('fish sandwich');
-------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Person` (
  `id` smallint UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL UNIQUE,
  `password` varchar(100) NOT NULL,
  `weight` smallint UNSIGNED NOT NULL,
  `height` smallint UNSIGNED NOT NULL,
  `age` smallint UNSIGNED NOT NULL,
  `gender` char(8) NOT NULL,
  PRIMARY KEY (`id`)
);


-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Goal` (
	`goal_number` smallint UNSIGNED NOT NULL AUTO_INCREMENT,
 	`id` smallint UNSIGNED NOT NULL,
  `target_weight` smallint UNSIGNED NOT NULL,
  `time_frame` smallint UNSIGNED NOT NULL,
  `goal_achieved` char(8) NOT NULL,
 	CONSTRAINT `PK_Goal` PRIMARY KEY (`goal_number`, `id`),
  FOREIGN KEY (`id`) REFERENCES Person (`id`) ON DELETE CASCADE
);


-------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Eats` (
  `meal_name` varchar(100) NOT NULL,
  `id` smallint UNSIGNED NOT NULL,
  `date` varchar(100) NOT NULL,
  CONSTRAINT `PK_Eats` PRIMARY KEY (`meal_name`, `id`, `date`),
  FOREIGN KEY (`meal_name`) REFERENCES Meal (`meal_name`),
  FOREIGN KEY (`id`) REFERENCES Person (`id`) ON DELETE CASCADE
);


-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Performs` (
 	`id` smallint UNSIGNED NOT NULL,
  `exercise_name` varchar(100) NOT NULL,
  `date` varchar(100) NOT NULL,
  `repetitions` smallint UNSIGNED NOT NULL,
 	CONSTRAINT `PK_Performs` PRIMARY KEY (`id`, `exercise_name`, `date`),
  FOREIGN KEY (`id`) REFERENCES Person (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`exercise_name`) REFERENCES Exercise (`exercise_name`)
);


-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Uses` (
 	`id` smallint UNSIGNED NOT NULL,
  `program_name` varchar(100) NOT NULL,
  `start_date` varchar(100) NOT NULL,
 	CONSTRAINT `PK_Uses` PRIMARY KEY (`id`, `program_name`, `start_date`),
  FOREIGN KEY (`id`) REFERENCES Person (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`program_name`) REFERENCES Program (`program_name`)
);
