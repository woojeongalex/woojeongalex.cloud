CREATE TABLE `Untitled10` (
	`id`	bigint	NOT NULL,
	`analysis_engine`	varchar	NULL,
	`tuning_accuracy`	int	NULL,
	`pitch_deviation_cents`	int	NULL,
	`summary`	varchar	NULL,
	`string_readings`	json	NULL,
	`analyzed_at`	timestamptz	NULL,
	`instrument_recording_id`	bigint	NOT NULL
);

CREATE TABLE `Untitled6` (
	`id`	bigint	NOT NULL,
	`analysis_engine`	varchar	NULL,
	`pitch_score`	int	NULL,
	`rhythm_score`	int	NULL,
	`vocal_grade`	varchar	NULL,
	`summary`	varchar	NULL,
	`analyzed_at`	timestamptz	NULL,
	`user_vocal_recording_id`	bigint	NOT NULL
);

CREATE TABLE `Untitled` (
	`id`	bigint	NOT NULL,
	`username`	varchar	NULL,
	`nickname`	varchar	NULL,
	`email`	varchar	NULL,
	`role`	varchar	NULL
);

CREATE TABLE `Untitled12` (
	`id`	bigint	NOT NULL,
	`topic_id`	varchar	NULL,
	`file_name`	varchar	NULL,
	`duration_sec`	int	NULL,
	`recorded_at`	timestamptz	NULL,
	`speech_evaluation_id`	bigint	NOT NULL,
	`user_id`	bigint	NOT NULL
);

CREATE TABLE `Untitled8` (
	`id`	bigint	NOT NULL,
	`created_at`	timestamptz	NULL,
	`user_id`	bigint	NOT NULL
);

CREATE TABLE `Untitled7` (
	`id`	bigint	NOT NULL,
	`vocalization_pattern`	varchar	NULL,
	`recommended_genres`	json	NULL,
	`recommended_songs`	json	NULL,
	`created_at`	timestamptz	NULL,
	`sing_evaluation_id`	bigint	NOT NULL,
	`ai_vocal_analysis_id`	bigint	NOT NULL
);

CREATE TABLE `Untitled9` (
	`id`	bigint	NOT NULL,
	`instrument_id`	varchar	NULL,
	`file_name`	varchar	NULL,
	`duration_sec`	int	NULL,
	`recorded_at`	timestamptz	NULL,
	`user_id`	bigint	NOT NULL,
	`instrument_evaluation_id`	bigint	NOT NULL
);

CREATE TABLE `Untitled3` (
	`id`	bigint	NOT NULL,
	`search_query`	varchar	NULL,
	`title`	varchar	NULL,
	`artist`	varchar	NULL,
	`bpm`	int	NULL,
	`song_key`	varchar	NULL,
	`range_label`	varchar	NULL,
	`mr_track_name`	varchar	NULL,
	`mr_description`	varchar	NULL,
	`created_at`	timestamptz	NULL,
	`catalog_song_id`	varchar	NOT NULL
);

CREATE TABLE `Untitled5` (
	`id`	bigint	NOT NULL,
	`input_source`	varchar	NULL,
	`file_name`	varchar	NULL,
	`duration_sec`	int	NULL,
	`content_type`	varchar	NULL,
	`storage_uri`	varchar	NULL,
	`recorded_at`	timestamptz	NULL,
	`user_id`	bigint	NOT NULL,
	`catalog_song_id`	varchar	NOT NULL,
	`mr_search_list_id`	bigint	NOT NULL,
	`sing_evaluation_id`	bigint	NOT NULL
);

CREATE TABLE `Untitled13` (
	`id`	bigint	NOT NULL,
	`analysis_engine`	varchar	NULL,
	`clarity_score`	int	NULL,
	`pace_score`	int	NULL,
	`tone_score`	int	NULL,
	`summary`	varchar	NULL,
	`feedback_points`	json	NULL,
	`analyzed_at`	timestamptz	NULL,
	`speech_recording_id`	bigint	NOT NULL
);

CREATE TABLE `Untitled4` (
	`id`	bigint	NOT NULL,
	`created_at`	timestamptz	NULL,
	`user_id`	bigint	NOT NULL
);

CREATE TABLE `Untitled11` (
	`id`	bigint	NOT NULL,
	`created_at`	timestamptz	NULL,
	`user_id`	bigint	NOT NULL
);

CREATE TABLE `Untitled2` (
	`catalog_song_id`	varchar	NOT NULL,
	`title`	varchar	NULL,
	`artist`	varchar	NULL,
	`bpm`	int	NULL,
	`song_key`	varchar	NULL,
	`range_label`	varchar	NULL,
	`mr_track_name`	varchar	NULL,
	`mr_description`	varchar	NULL
);

ALTER TABLE `Untitled10` ADD CONSTRAINT `PK_UNTITLED10` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled6` ADD CONSTRAINT `PK_UNTITLED6` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled` ADD CONSTRAINT `PK_UNTITLED` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled12` ADD CONSTRAINT `PK_UNTITLED12` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled8` ADD CONSTRAINT `PK_UNTITLED8` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled7` ADD CONSTRAINT `PK_UNTITLED7` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled9` ADD CONSTRAINT `PK_UNTITLED9` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled3` ADD CONSTRAINT `PK_UNTITLED3` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled5` ADD CONSTRAINT `PK_UNTITLED5` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled13` ADD CONSTRAINT `PK_UNTITLED13` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled4` ADD CONSTRAINT `PK_UNTITLED4` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled11` ADD CONSTRAINT `PK_UNTITLED11` PRIMARY KEY (
	`id`
);

ALTER TABLE `Untitled2` ADD CONSTRAINT `PK_UNTITLED2` PRIMARY KEY (
	`catalog_song_id`
);

