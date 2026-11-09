# Milestone 3 content: the first batch of about 40 concepts, written in chunks of about 10.
# Written against the August 2026 exam guide and docs read 2026-11-06. Each concept's EVIDENCE lists
# (source index, regex) pairs that factcheck.py tests against the live doc pages it links.
D = 'https://docs.databricks.com/aws/en'
EVIDENCE = {}

def chunk1(concept, opt):
  C = []
  # ---------- 2.1 triggered vs continuous ----------
  PM = {'sched': 'Triggered mode, run by a scheduled job', 'cjob': 'Triggered mode, run by a continuous job',
        'cmode': 'Continuous pipeline mode, with no job', 'manual': 'Triggered mode, started by hand each day',
        'interval': 'Continuous mode, 24-hour trigger interval'}
  C.append(concept('dea-2-1-pipeline-modes', '2', '2.1', 11, 'Triggered or continuous ingestion',
    [{'title': 'Triggered vs. continuous pipeline mode', 'url': D + '/ldp/concepts/pipeline-mode'},
     {'title': 'Ingest with SQL and Spark APIs', 'url': D + '/ingestion/'}],
    [
      {'id': 'r1', 'type': 'decision', 'prompt': 'A Lakeflow Declarative Pipeline ingests orders that analysts read once each morning, and cost matters more than latency. Triggered or continuous mode?', 'answer': 'Triggered', 'why': 'It processes the data available when the update starts, then stops, so compute runs only for the update.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'A triggered Lakeflow Declarative Pipeline update starts at 06:00. Which data does it process?', 'answer': 'The data available when the update started', 'why': 'It refreshes every table from that data and stops; anything arriving later waits for the next update.'},
      {'id': 'r3', 'type': 'comparison', 'prompt': 'In a Lakeflow Declarative Pipeline, triggered or continuous mode: which needs an always-running cluster?', 'answer': 'Continuous', 'why': 'It processes data as it arrives and runs until stopped; triggered mode stops when the update completes.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'A Lakeflow Declarative Pipeline set to triggered mode runs as a task in a continuous job. How does it run?', 'answer': 'Continuously', 'why': 'When a job orchestrates a pipeline, the job’s execution mode takes precedence over the pipeline’s own mode setting.'},
      {'id': 'r5', 'type': 'cloze', 'text': 'For a continuous Lakeflow Declarative Pipeline, Databricks recommends a continuous {{gap}} rather than setting the pipeline mode to continuous.', 'answer': 'job', 'why': 'The job manages the pipeline’s lifecycle; leave the pipeline’s own mode at triggered, the default.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A Lakeflow Declarative Pipeline ingests point-of-sale files into bronze. Finance reads the tables once each morning, and the team wants to pay for compute only while data is being processed.\n\nHow should the pipeline run?', 'pick': 1,
       'correct': [opt(PM['sched'], 'Each run processes what has arrived and stops, so compute runs only during the update.')],
       'distractors': [opt(PM['cjob'], 'Runs the pipeline continuously, keeping compute up all day for a once-a-day read.'),
                       opt(PM['cmode'], 'Keeps an always-running cluster, which is the cost the team wants to avoid.'),
                       opt(PM['manual'], 'Also processes and stops, but relies on someone starting it every morning.'),
                       opt(PM['interval'], 'Continuous mode still keeps a cluster running between updates.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A Lakeflow Declarative Pipeline ingests card-payment events into bronze. Fraud analysts need new events in the table within a minute, around the clock, and the team follows Databricks’ recommended setup.\n\nHow should the pipeline run?', 'pick': 1,
       'correct': [opt(PM['cjob'], 'A continuous job runs the pipeline continuously and is the recommended pattern; the pipeline’s own mode stays triggered.')],
       'distractors': [opt(PM['sched'], 'New events would wait until the next scheduled run.'),
                       opt(PM['cmode'], 'Works, but Databricks discourages the built-in continuous mode for new pipelines.'),
                       opt(PM['manual'], 'Can’t keep events within a minute around the clock.'),
                       opt(PM['interval'], 'A 24-hour interval misses the one-minute target.')]},
      {'id': 's3', 'stem': 'A Lakeflow Declarative Pipeline has run in continuous mode for months, but its dashboard is now checked once a week and the team wants to cut cost.\n\nHow should the pipeline run from now on?', 'pick': 1,
       'correct': [opt(PM['sched'], 'A weekly scheduled run processes the new data and stops, so nothing runs in between.')],
       'distractors': [opt(PM['cjob'], 'Still runs all the time, which is the cost to cut.'),
                       opt(PM['cmode'], 'That’s the current setup, with its always-running cluster.'),
                       opt(PM['manual'], 'Works, but leaves the weekly refresh to someone remembering.'),
                       opt(PM['interval'], 'Continuous mode keeps a cluster running between updates.')]},
    ], setting=['Lakeflow Declarative Pipeline'], rev=1))
  EVIDENCE['dea-2-1-pipeline-modes'] = [(0, r'stops after refreshing all tables based on the data available when the update started'),
    (0, r'Continuous pipelines require an always-running cluster'), (0, r'recommends running continuous pipelines with a \[continuous job\]'),
    (0, r'job determines the execution mode and takes precedence'), (0, r'set the pipeline\'s \*\*Pipeline mode\*\* to triggered \(the default\)'),
    (0, r'discourages its use for new pipelines'), (0, r'is used only with continuous pipelines'), (1, r'Batch ingestion \| \[Triggered\]')]

  # ---------- 2.1 local file upload ----------
  C.append(concept('dea-2-1-file-upload', '2', '2.1', 12, 'Creating a table from local files',
    [{'title': 'Create or modify a table using file upload', 'url': D + '/ingestion/create-or-modify-table'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'On Databricks’ Create or modify a table using file upload page, how many files can one upload hold, and how large can they be?', 'answer': 'Up to 10 files, under 2 GB in total', 'why': 'The page is for small files from your machine; files already in cloud storage load with the add data UI or COPY INTO.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'A colleague tries to load a zipped CSV through Databricks file upload. What happens?', 'answer': 'It isn’t accepted: compressed files aren’t supported', 'why': 'File upload takes uncompressed CSV, TSV, JSON, Avro, Parquet and text files only.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'What kind of table does Databricks file upload create?', 'answer': 'A managed Delta table', 'why': 'It creates or overwrites a managed Delta table in the schema you pick, in Unity Catalog or the legacy Hive metastore.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Three CSV files with the same columns go into one Databricks file upload. How are they combined?', 'answer': 'Appended as rows of one table', 'why': 'Uploaded files combine by appending; joining or merging records during upload isn’t supported.'},
      {'id': 'r5', 'type': 'cloze', 'text': 'In Databricks file upload, turning off automatic column type detection makes every column {{gap}}.', 'answer': 'STRING', 'why': 'Type detection is on by default for CSV and JSON; you can still edit each column’s type in the preview.'},
    ], setting=['file upload'], rev=1))
  EVIDENCE['dea-2-1-file-upload'] = [(0, r'supports uploading up to 10 files at a time'), (0, r'must be under 2 gigabytes'),
    (0, r'Compressed files such as `zip` and `tar` files are not supported'), (0, r'create or overwrite a managed Delta Lake table'),
    (0, r'combine by appending all data as rows'), (0, r'all column types are inferred as `STRING`')]

  # ---------- 2.4 database connector components ----------
  C.append(concept('dea-2-4-database-connector-parts', '2', '2.4', 13, 'Parts of a Lakeflow Connect database connector',
    [{'title': 'Managed database connectors', 'url': D + '/ingestion/lakeflow-connect/cdc-overview'},
     {'title': 'Lakeflow Connect connector concepts', 'url': D + '/ingestion/lakeflow-connect/'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In a Lakeflow Connect database connector, which component runs continuously, and on what compute?', 'answer': 'The ingestion gateway, on classic compute', 'why': 'It captures changes before the source truncates its change logs, so you pay for it even while the pipeline is idle.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'In a Lakeflow Connect database connector, where does extracted data wait before the ingestion pipeline applies it?', 'answer': 'In a staging volume in Unity Catalog', 'why': 'Staging lets the pipeline run on any schedule while the gateway keeps capturing; data is purged after 30 days.'},
      {'id': 'r3', 'type': 'comparison', 'prompt': 'In Lakeflow Connect, SaaS connector or database connector: which adds an ingestion gateway and staging storage?', 'answer': 'The database connector', 'why': 'SaaS connectors use a connection, an ingestion pipeline and destination tables only.', 'src': 1},
      {'id': 'r4', 'type': 'basic', 'prompt': 'What kind of table does a Lakeflow Connect ingestion pipeline write to?', 'answer': 'Streaming tables', 'why': 'Delta tables with extra support for incremental processing; the pipeline itself runs on serverless compute.'},
      {'id': 'r5', 'type': 'symptom', 'prompt': 'A Lakeflow Connect database connector’s ingestion pipeline runs once a day, yet compute costs build up around the clock. Likely cause?', 'answer': 'The ingestion gateway runs continuously on classic compute', 'why': 'The gateway keeps capturing changes between pipeline runs, so its compute is always provisioned.'},
    ],
    [
      {'id': 's1', 'stem': 'A team adds a Lakeflow Connect managed connector for a PostgreSQL database. Compared with their existing Salesforce connector, it brings two extra components.\n\nWhich two?', 'pick': 2,
       'correct': [opt('An ingestion gateway on classic compute', 'Database connectors need it to capture changes continuously; SaaS connectors don’t.'),
                   opt('A staging volume in Unity Catalog', 'Buffers the gateway’s extracted data for the pipeline; SaaS connectors have none.')],
       'distractors': [opt('A Unity Catalog connection to the source', 'Every connector has one; the Salesforce connector uses a connection too.'),
                       opt('An ingestion pipeline on serverless', 'Both connector types have an ingestion pipeline.'),
                       opt('Streaming tables as the destination', 'Both connector types write to streaming tables.'),
                       opt('A job for each pipeline schedule', 'Lakeflow Connect creates a job per schedule for both connector types.')]},
      {'id': 's2', 'stem': 'A Lakeflow Connect database connector ingests SQL Server changes on an hourly schedule. The DBA warns that the source truncates its change logs every 20 minutes.\n\nWhich component keeps changes from being lost between runs?', 'pick': 1,
       'correct': [opt('The ingestion gateway, running continuously', 'It captures changes as they happen, before the source truncates its logs.')],
       'distractors': [opt('The ingestion pipeline, run every hour', 'Runs hourly, so by itself it would miss truncated changes.'),
                       opt('The Unity Catalog connection object', 'Stores credentials; it doesn’t capture anything.'),
                       opt('The destination streaming tables', 'Receive changes only when the pipeline runs.'),
                       opt('The job created for the schedule', 'Starts the hourly pipeline run; it doesn’t capture changes.')]},
      {'id': 's3', 'stem': 'A Lakeflow Connect database connector’s ingestion pipeline is paused for a week while a schema change is reviewed. The gateway keeps running.\n\nWhere do the changes captured that week wait?', 'pick': 1,
       'correct': [opt('In the staging volume, kept up to 30 days', 'The gateway writes extracted data to staging, which is purged after 30 days.')],
       'distractors': [opt('In the source database’s change log', 'The source may truncate it; the gateway has already extracted the changes.'),
                       opt('In the destination streaming tables', 'Nothing reaches them until the pipeline runs again.'),
                       opt('In the ingestion pipeline’s event log', 'The event log records pipeline events, not change data.'),
                       opt('In the gateway’s classic compute memory', 'The gateway writes what it extracts to staging storage.')]},
    ], setting=['Lakeflow Connect'], rev=1))
  EVIDENCE['dea-2-4-database-connector-parts'] = [(0, r'The gateway runs on classic compute, and it runs continuously'),
    (0, r'Data is automatically purged from staging after 30 days'), (0, r'The pipeline runs on serverless compute'),
    (0, r'you provision and pay for its classic compute even when your ingestion pipeline is idle'), (0, r'These are \[streaming tables\]'),
    (1, r'SaaS and file connectors use a connection, an ingestion pipeline, and destination tables'),
    (1, r'Lakeflow Connect automatically creates a \[job\]')]

  # ---------- 2.4 history tracking ----------
  HT = {'scd1': 'History tracking off (SCD type 1)', 'scd2': 'History tracking on (SCD type 2)', 'append': 'Append-only ingestion of every row',
        'snap': 'A full snapshot reload on each run', 'mv': 'A materialized view over the target'}
  C.append(concept('dea-2-4-history-tracking', '2', '2.4', 14, 'History tracking in managed connectors',
    [{'title': 'Enable history tracking (SCD type 2)', 'url': D + '/ingestion/lakeflow-connect/scd'},
     {'title': 'Query-based connectors', 'url': D + '/ingestion/lakeflow-connect/query-based-overview'},
     {'title': 'Managed database connectors', 'url': D + '/ingestion/lakeflow-connect/cdc-overview'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'What is the default history tracking setting for a Lakeflow Connect managed ingestion pipeline?', 'answer': 'Off: SCD type 1', 'why': 'Updates and deletes at the source overwrite the destination rows; turning history tracking on gives SCD type 2.'},
      {'id': 'r2', 'type': 'code', 'prompt': 'In a Lakeflow Connect pipeline defined in a bundle, keep every past version of each row.', 'lang': 'yaml', 'code': 'ingestion_definition:\n  connection_name: crm_conn\n  objects:\n    - table:\n        source_table: accounts\n        table_configuration:\n          scd_type: {{gap}}', 'answer': 'SCD_TYPE_2', 'why': '`SCD_TYPE_2` turns history tracking on; `SCD_TYPE_1`, the default, keeps only the latest row.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'A Lakeflow Connect pipeline has history tracking on. A customer’s email changes at the source. What happens in the destination?', 'answer': 'A new row is added and the old one is marked inactive', 'why': 'SCD type 2 keeps every version, so you can tell which row is current.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'A table is dropped at the source of a Lakeflow Connect pipeline with history tracking off. What happens to its destination table?', 'answer': 'Nothing: its data stays', 'why': 'Deleting a table or column at the source never deletes it from the destination, even with SCD type 1.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A Lakeflow Connect pipeline ingests Salesforce accounts into Unity Catalog. Auditors must be able to see what each account looked like on any past date.\n\nWhich setting fits?', 'pick': 1,
       'correct': [opt(HT['scd2'], 'Keeps every version of each account and marks which one is current.')],
       'distractors': [opt(HT['scd1'], 'Overwrites each row with its latest values, so past versions are lost.'),
                       opt(HT['append'], 'A query-based connector mode; it piles up rows without marking which was current.'),
                       opt(HT['snap'], 'Replaces the table each run, so past versions are lost.'),
                       opt(HT['mv'], 'Recomputes from the target, which only holds what was ingested.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A Lakeflow Connect pipeline ingests Salesforce accounts for a dashboard that only ever shows each account’s current details. Storage should stay as small as possible.\n\nWhich setting fits?', 'pick': 1,
       'correct': [opt(HT['scd1'], 'The default: each row is overwritten with its latest values, so only current data is stored.')],
       'distractors': [opt(HT['scd2'], 'Keeps every past version, growing storage for history nobody reads.'),
                       opt(HT['append'], 'Adds a row for every change read, so storage keeps growing.'),
                       opt(HT['snap'], 'Rereads the whole source each run instead of only the changes.'),
                       opt(HT['mv'], 'Adds a second copy of the data on top of the ingested table.')]},
      {'id': 's3', 'stem': 'A Lakeflow Connect pipeline ingests a SQL Server customer table. Compliance needs every version of each customer’s address, with the period each version was valid.\n\nWhich setting fits?', 'pick': 1,
       'correct': [opt(HT['scd2'], 'Keeps each version and records when it was active, using the sequence column.')],
       'distractors': [opt(HT['scd1'], 'Keeps only the latest address for each customer.'),
                       opt(HT['append'], 'Keeps rows but records no validity period for them.'),
                       opt(HT['snap'], 'Reloads the current table, so earlier addresses disappear.'),
                       opt(HT['mv'], 'Can only show what the ingested table already holds.')]},
    ], setting=['Lakeflow Connect'], rev=1))
  EVIDENCE['dea-2-4-history-tracking'] = [(0, r'By default, history tracking is off \(SCD type 1\)'), (0, r'`SCD_TYPE_2`: History tracking on'),
    (0, r'Deleting a table or column in the source does not delete that data from the destination, even when SCD type 1 is selected'),
    (0, r'keeps the old row and adds the update as a new row. It marks the old row as inactive'), (0, r'time span that each row version was active'),
    (0, r'scd_type: SCD_TYPE_2'), (1, r'APPEND\\_ONLY'), (2, r'change data capture \(CDC\) or full snapshot')]

  # ---------- 2.6 choosing an ingestion method ----------
  IM = {'mc': 'A Lakeflow Connect managed connector', 'al': 'Auto Loader in a declarative pipeline', 'fed': 'Lakehouse Federation, with no copy',
        'qb': 'A Lakeflow Connect query-based connector', 'jdbc': 'A notebook reading the source over JDBC', 'copy': 'A scheduled `COPY INTO` command'}
  C.append(concept('dea-2-6-choose-ingestion', '2', '2.6', 15, 'Choosing an ingestion method',
    [{'title': 'What is Lakeflow Connect?', 'url': D + '/ingestion/overview'},
     {'title': 'Ingest with SQL and Spark APIs', 'url': D + '/ingestion/'},
     {'title': 'Query-based connectors', 'url': D + '/ingestion/lakeflow-connect/query-based-overview'},
     {'title': 'File connectors', 'url': D + '/ingestion/lakeflow-connect/file-connectors-overview'},
     {'title': 'Managed SaaS connectors', 'url': D + '/ingestion/lakeflow-connect/saas-overview'},
     {'title': 'Connect to external databases and catalogs', 'url': D + '/query-federation/'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'When choosing how to ingest a source into Databricks, which layer does Databricks recommend trying first?', 'answer': 'The most managed one: a managed connector', 'why': 'Drop to Lakeflow pipelines or Structured Streaming only when the managed layer can’t meet the need, such as an unsupported source.'},
      {'id': 'r2', 'type': 'decision', 'prompt': 'A SQL analyst wants to ingest new JSON files from cloud storage incrementally, in SQL only. What does Databricks recommend over COPY INTO?', 'answer': '`CREATE STREAMING TABLE` with `read_files`', 'why': 'Databricks calls the streaming table the scalable, recommended alternative to COPY INTO for SQL users.', 'src': 1},
      {'id': 'r3', 'type': 'decision', 'prompt': 'Analysts want to query a PostgreSQL table from Databricks now and then, without ingesting a copy. Which feature fits?', 'answer': 'Lakehouse Federation', 'why': 'Governed, read-only queries through a foreign catalog, pushed down to the source, with nothing copied.', 'src': 5},
      {'id': 'r4', 'type': 'decision', 'prompt': 'A database has no change data capture, but every table has an `updated_at` column. Which Lakeflow Connect option can ingest it incrementally?', 'answer': 'A query-based connector', 'why': 'It reads rows past the last high-water mark of a cursor column, with no gateway or staging volume.', 'src': 2},
      {'id': 'r5', 'type': 'comparison', 'prompt': 'To ingest files with Lakeflow Connect, standard or managed file connectors: which use Spark and SQL APIs such as Auto Loader and `COPY INTO`?', 'answer': 'Standard file connectors', 'why': 'Managed file connectors, for sources such as SharePoint and Google Drive, handle authentication, incremental reads and retries for you.', 'src': 3},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A retailer must ingest its Salesforce opportunities into Unity Catalog every hour for reporting. Databricks supports Salesforce, and the team has no capacity to maintain API code.\n\nWhich option should they use?', 'pick': 1,
       'correct': [opt(IM['mc'], 'Handles Salesforce authentication, incremental reads, schema evolution and retries with no code.')],
       'distractors': [opt(IM['al'], 'Reads files from cloud storage; Salesforce isn’t a file source.'),
                       opt(IM['fed'], 'Leaves the data in the source, but the reporting needs an ingested copy.'),
                       opt(IM['qb'], 'Built for databases with a cursor column, not SaaS APIs.'),
                       opt(IM['jdbc'], 'Means writing and maintaining custom code, which the team can’t take on.'),
                       opt(IM['copy'], 'Loads files from cloud storage, not records from a SaaS API.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A retailer must ingest a niche ticketing system into Unity Catalog every hour. Databricks has no connector for it, but the system exports JSON files to S3 every hour.\n\nWhich option should they use?', 'pick': 1,
       'correct': [opt(IM['al'], 'The data lands as files in cloud storage, which Auto Loader ingests incrementally.')],
       'distractors': [opt(IM['mc'], 'No managed connector exists for this system.'),
                       opt(IM['fed'], 'Federation queries databases in place; these are files.'),
                       opt(IM['qb'], 'Needs a database with a cursor column; this source delivers files.'),
                       opt(IM['jdbc'], 'The system exposes files, not a JDBC database.'),
                       opt(IM['copy'], 'Also loads files, but Databricks now recommends Auto Loader in a pipeline or a streaming table.')]},
      {'id': 's3', 'stem': 'Instead of ingesting, finance analysts want a weekly look at a few Oracle tables from Databricks SQL, governed in Unity Catalog, without copying the data.\n\nWhich option should they use?', 'pick': 1,
       'correct': [opt(IM['fed'], 'Read-only, governed queries through a foreign catalog, with nothing copied.')],
       'distractors': [opt(IM['mc'], 'Copies the tables into Delta, which they don’t want.'),
                       opt(IM['al'], 'Ingests files from cloud storage, not Oracle tables.'),
                       opt(IM['qb'], 'Copies changed rows into streaming tables, which they don’t want.'),
                       opt(IM['jdbc'], 'Loads data in a notebook, governed only at the connection level.'),
                       opt(IM['copy'], 'Loads files into a table, copying data they want left in place.')]},
      {'id': 's4', 'flip': 's5', 'stem': 'A team must ingest a MySQL application database into Unity Catalog. The DBA won’t enable binlog change capture, but every table has a reliable `modified_at` column.\n\nWhich option should they use?', 'pick': 1,
       'correct': [opt(IM['qb'], 'Reads rows past the last high-water mark of a cursor column, with no change capture needed.')],
       'distractors': [opt(IM['mc'], 'The managed database connector relies on change data capture, which the DBA won’t enable.'),
                       opt(IM['fed'], 'Queries in place; it doesn’t ingest the tables into Unity Catalog.'),
                       opt(IM['al'], 'Reads files, not a live database.'),
                       opt(IM['jdbc'], 'Possible, but means custom incremental logic to build and maintain.'),
                       opt(IM['copy'], 'Loads files from cloud storage, not database tables.')]},
      {'id': 's5', 'flip': 's4', 'stem': 'A team must ingest a MySQL application database into Unity Catalog, capturing every insert, update and delete. The DBA has enabled binlog change capture for Databricks.\n\nWhich option should they use?', 'pick': 1,
       'correct': [opt(IM['mc'], 'Uses change data capture to apply every insert, update and delete incrementally.')],
       'distractors': [opt(IM['qb'], 'Captures only the latest state at each run, and deletes need extra configuration.'),
                       opt(IM['fed'], 'Queries in place; nothing is ingested.'),
                       opt(IM['al'], 'Reads files, not a database’s change log.'),
                       opt(IM['jdbc'], 'Would need custom change capture code to build and maintain.'),
                       opt(IM['copy'], 'Loads files from cloud storage, not database changes.')]},
    ], setting=['ingest'], rev=1))
  EVIDENCE['dea-2-6-choose-ingestion'] = [(0, r'Databricks recommends starting with the most managed layer'),
    (1, r'recommended alternative to `COPY INTO`'), (1, r'Databricks recommends starting with the most managed layer'),
    (2, r'cursor column'), (2, r'doesn\'t require an ingestion gateway or a staging volume'), (2, r'even if it doesn\'t support CDC or binlog access'),
    (2, r'Soft-deletion tracking is supported using `deletion_condition`'), (2, r'They only capture the latest state'),
    (3, r'Standard file connectors use Spark and SQL APIs'), (3, r'Ingest files from S3, ADLS, or GCS using Auto Loader or `COPY INTO`'),
    (3, r'Managed file connectors handle authentication for each source, incremental reads, and automated retries'),
    (4, r'handles source-specific authentication, incremental reads, schema evolution, and automated retries'),
    (5, r'governed, read-only access to external data through Unity Catalog foreign catalogs, with automatic query pushdown'), (5, r'\[Oracle\]')]

  # ---------- 2.5 JDBC and Spark data sources ----------
  JD = {'uc': 'A JDBC Unity Catalog connection', 'fed': 'A Lakehouse Federation foreign catalog', 'bund': 'The bundled `postgresql` Spark connector',
        'jar': 'A third-party connector installed on the cluster', 'mc': 'A Lakeflow Connect managed connector'}
  C.append(concept('dea-2-5-jdbc-in-notebooks', '2', '2.5', 16, 'Reading databases from notebooks over JDBC',
    [{'title': 'Spark data sources', 'url': D + '/connect/spark-data-sources'},
     {'title': 'JDBC connection', 'url': D + '/connect/jdbc-connection'},
     {'title': 'Connect to external databases and catalogs', 'url': D + '/query-federation/'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In a notebook, read a table through the JDBC Unity Catalog connection `erp_conn`.', 'lang': 'python', 'code': 'df = (spark.read\n  .format("jdbc")\n  .option("{{gap}}",\n    "erp_conn")\n  .option("dbtable", "dbo.invoices")\n  .load())', 'answer': 'databricks.connection', 'why': 'The connection holds the driver, URL and credentials, which stay hidden from the person querying.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'A notebook reads SQL Server through a Spark data source with the `query` option. Where does that SQL run?', 'answer': 'Entirely on the source database', 'why': 'Spark fetches only the result and doesn’t push its own transformations into that query.'},
      {'id': 'r3', 'type': 'decision', 'prompt': 'A notebook on serverless compute must read a database over JDBC with a driver that isn’t bundled in the runtime. Which option works?', 'answer': 'A JDBC Unity Catalog connection', 'why': 'Custom driver JARs can’t be installed on serverless; the connection loads the driver from a Unity Catalog volume.'},
      {'id': 'r4', 'type': 'comparison', 'prompt': 'For reading an external database, a JDBC Unity Catalog connection or Lakehouse Federation: which governs access per table?', 'answer': 'Lakehouse Federation', 'why': 'A foreign catalog gives table-level access control; a JDBC connection governs only at the connection level.', 'src': 1},
      {'id': 'r5', 'type': 'basic', 'prompt': 'In a Spark data source read from a notebook, where should the database password come from?', 'answer': 'A secret, read with `dbutils.secrets.get`', 'why': 'The docs’ examples read the user and password from a secret scope instead of putting them in code.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A nightly Lakeflow Jobs task runs a notebook on serverless compute that writes cleaned results back into a partner’s PostgreSQL database over JDBC. The credentials must stay hidden from the notebook’s authors.\n\nWhich approach fits?', 'pick': 1,
       'correct': [opt(JD['uc'], 'Works on serverless, supports writes, and keeps the credentials inside a Unity Catalog object.')],
       'distractors': [opt(JD['fed'], 'Read-only: query federation doesn’t support writes.'),
                       opt(JD['bund'], 'Can write to PostgreSQL, but the notebook must supply the credentials itself.'),
                       opt(JD['jar'], 'Custom connector JARs can’t be installed on serverless compute.'),
                       opt(JD['mc'], 'Ingests into Databricks; it doesn’t write back to the source.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'Analysts need weekly, read-only access to a partner’s PostgreSQL tables from Databricks SQL, with access controlled per table in Unity Catalog. A colleague suggests a JDBC read in a notebook.\n\nWhich approach fits best?', 'pick': 1,
       'correct': [opt(JD['fed'], 'Databricks recommends query federation here: table-level access control and automatic pushdown.')],
       'distractors': [opt(JD['uc'], 'Governs access only at the connection level, not per table.'),
                       opt(JD['bund'], 'A notebook read with no per-table governance in Unity Catalog.'),
                       opt(JD['jar'], 'A notebook-only route with no per-table governance.'),
                       opt(JD['mc'], 'Copies the tables in, which a read-only weekly look doesn’t need.')]},
      {'id': 's3', 'stem': 'A notebook on a dedicated cluster must read MongoDB collections through the Spark data source API. MongoDB has no bundled Databricks connector, no JDBC driver here, and no Lakeflow Connect connector.\n\nWhich approach fits?', 'pick': 1,
       'correct': [opt(JD['jar'], 'On dedicated compute you can install third-party Spark connectors, such as MongoDB’s.')],
       'distractors': [opt(JD['uc'], 'Needs a JDBC driver, which this source doesn’t offer here.'),
                       opt(JD['fed'], 'MongoDB isn’t a query federation source.'),
                       opt(JD['bund'], 'A PostgreSQL connector can’t read MongoDB.'),
                       opt(JD['mc'], 'There’s no managed connector for this source.')]},
    ], setting=['JDBC', 'Spark data source'], rev=1))
  EVIDENCE['dea-2-5-jdbc-in-notebooks'] = [(0, r'specified SQL statement runs entirely on the external data source'),
    (0, r'specify `databricks.connection` in your Spark options'), (0, r'Hide connection credentials from the querying user'),
    (0, r'Custom third-party Spark JARs are not supported on Databricks SQL, serverless'), (0, r'MongoDB, Cassandra'),
    (0, r'dbutils\.secrets\.get'), (0, r'\| PostgreSQL \| `"postgresql"` \|'), (0, r'Writes on serverless compute are supported for PostgreSQL'),
    (1, r'JDBC Unity Catalog connection provides governance only at the connection level'), (1, r'query federation doesn\'t support writes'),
    (1, r'reads and installs the JDBC driver JAR from a Unity Catalog volume'), (2, r'\[PostgreSQL\]')]

  # ---------- 2.7 VARIANT, STRUCT or JSON string ----------
  VA = {'var': '`VARIANT`, built with `parse_json`', 'str': 'A JSON `STRING` column', 'struct': 'A `STRUCT` parsed with `from_json`',
        'map': 'A `MAP<STRING, STRING>` column', 'flat': 'Arrays exploded into separate rows'}
  C.append(concept('dea-2-7-variant-json', '2', '2.7', 17, 'Storing nested JSON: VARIANT, STRUCT or string',
    [{'title': 'Query variant data', 'url': D + '/semi-structured/variant'},
     {'title': 'Model semi-structured data', 'url': D + '/semi-structured/'},
     {'title': 'How is variant different than JSON strings?', 'url': D + '/semi-structured/variant-json-diff'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In Databricks SQL, store a JSON string column as `VARIANT`.', 'lang': 'sql', 'code': 'CREATE TABLE iot.bronze.readings AS\nSELECT device_id,\n  {{gap}}(body) AS reading\nFROM iot.raw.messages;', 'answer': 'parse_json', 'why': '`parse_json` turns a JSON string into `VARIANT`, which Databricks recommends over storing JSON strings.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'A `VARIANT` column `v` holds `{"user": {"Id": 7}}`. What does `v:user.id` return?', 'answer': 'NULL', 'why': 'Variant field names are case sensitive, so `id` doesn’t match `Id`, and a missing path returns NULL.'},
      {'id': 'r3', 'type': 'code', 'prompt': 'In Databricks SQL, return the first element of the `items` array inside a `VARIANT` column.', 'lang': 'sql', 'code': 'SELECT order_id,\n  payload:items{{gap}} AS first_item\nFROM shop.bronze.orders;', 'answer': '[0]', 'why': 'Variant paths use dots for fields and zero-based brackets for arrays; an index out of range returns NULL.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Can a Databricks `VARIANT` column be a table’s clustering key?', 'answer': 'No', 'why': 'VARIANT can’t be a clustering, partition or Z-order key, and can’t be used for grouping, ordering or comparisons.'},
      {'id': 'r5', 'type': 'comparison', 'prompt': 'For nested JSON in a Delta table, `STRUCT` or `VARIANT`: which gives the best read performance for a well-known, stable schema?', 'answer': '`STRUCT`', 'why': 'Each struct field is stored as a column with statistics; variant trades some of that for flexibility.', 'src': 1},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A bronze table receives clickstream events as JSON whose nested fields vary by event type and change often. Analysts query a few fields by path, and the team wants Databricks’ recommended type for flexible semi-structured data.\n\nHow should the payload be stored?', 'pick': 1,
       'correct': [opt(VA['var'], 'Flexible like a JSON string, with an optimized encoding that reads and writes faster.')],
       'distractors': [opt(VA['str'], 'Works, but Databricks recommends `VARIANT` instead; strings are slowest to read.'),
                       opt(VA['struct'], 'Enforces a fixed schema on write, which breaks as fields keep changing.'),
                       opt(VA['map'], 'Turns every value into a string and flattens nested types.'),
                       opt(VA['flat'], 'Changes the table’s grain rather than storing the payload.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A bronze table receives supplier records as JSON with a fixed, documented schema that hasn’t changed in years. Only validated records may be written, and downstream queries need the fastest reads.\n\nHow should the payload be stored?', 'pick': 1,
       'correct': [opt(VA['struct'], 'Types are enforced on write, and each field is stored as a column with statistics, so reads are fastest.')],
       'distractors': [opt(VA['var'], 'Flexible, but for a well-known schema structs read faster and validate on write.'),
                       opt(VA['str'], 'Stores no types and is the slowest to read.'),
                       opt(VA['map'], 'Collects no statistics and gives every value the same type.'),
                       opt(VA['flat'], 'Changes the grain; it isn’t a way to store the payload.')]},
      {'id': 's3', 'stem': 'A table stores raw JSON as a `STRING` column. Path queries with `:` have become slow, the fields keep changing, and the team doesn’t want to fix a schema.\n\nWhat should the payload become?', 'pick': 1,
       'correct': [opt(VA['var'], 'Keeps the flexibility of JSON strings with an encoding that outperforms them on reads and writes.')],
       'distractors': [opt(VA['str'], 'That’s the current, slowest-to-read setup.'),
                       opt(VA['struct'], 'Needs a fixed schema, which this data doesn’t have.'),
                       opt(VA['map'], 'Types every value as a string and collects no statistics.'),
                       opt(VA['flat'], 'Doesn’t speed up path queries on the payload.')]},
    ], setting=['VARIANT', 'JSON'], rev=1))
  EVIDENCE['dea-2-7-variant-json'] = [(0, r'Databricks recommends using `VARIANT` over JSON strings'), (0, r'use the `parse_json` function'),
    (0, r'Field names are always case sensitive'), (0, r'result is `NULL` of type `VARIANT`'), (0, r'raw:store\.fruit\[0\]'),
    (0, r'array-index is out of bounds, the result is null'), (0, r'cannot be used for clustering keys, partitions, or Z-order keys'),
    (0, r'cannot be used for comparisons, grouping, ordering'), (1, r'Best on read, but degrades past hundreds of columns'),
    (1, r'Enforced on write'), (1, r'Worst on read'), (1, r'outperforms JSON strings for reads and writes'), (1, r'statistics can\'t be collected'),
    (1, r'Less flexible|less flexible for schema evolution'), (2, r'recommends variant as a replacement for storing semi-structured data using JSON strings')]

  # ---------- 2.7 unstructured files with read_files ----------
  C.append(concept('dea-2-7-binary-files', '2', '2.7', 18, 'Ingesting unstructured files as binaryFile',
    [{'title': 'read_files table-valued function', 'url': D + '/sql/language-manual/functions/read_files'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In a streaming table, ingest PDF contracts from a volume with `read_files`, one row per file.', 'lang': 'sql', 'code': "CREATE OR REFRESH STREAMING TABLE\n  contracts_bronze\nAS SELECT * FROM STREAM read_files(\n  '/Volumes/legal/raw/contracts',\n  format => '{{gap}}');", 'answer': 'binaryFile', 'why': 'It returns one row per file with its path, modification time, length and raw bytes.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'Which four columns does `read_files` return for the `binaryFile` format?', 'answer': '`path`, `modificationTime`, `length`, `content`', 'why': 'The schema is fixed: `content` holds the file’s bytes as `BINARY`.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'A `read_files` query over a folder of images only needs file metadata. How do you leave out the bytes?', 'answer': '`SELECT * EXCEPT (content)`', 'why': '`content` holds each file’s binary data; the other columns are path, modification time and size.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Does `schemaEvolutionMode` apply when `read_files` reads `binaryFile` sources?', 'answer': 'No: the schema is fixed', 'why': 'Schema evolution doesn’t apply to `text` and `binaryFile`, which always return the same columns.'},
    ], setting=['read_files'], rev=1))
  EVIDENCE['dea-2-7-binary-files'] = [(0, r'`BINARYFILE`: Returns a fixed schema'), (0, r'\| `modificationTime` \| `TIMESTAMP`'),
    (0, r'\| `content` \| `BINARY`'), (0, r'Use `\* EXCEPT \(content\)`'), (0, r'This option doesn\'t apply to `text` and `binaryFile` files'),
    (0, r'leverages Auto Loader when used in a streaming table query')]

  # ---------- 2.3 schema hints and the rescued data column ----------
  SH = {'hint': 'Set `cloudFiles.schemaHints` for the column', 'infer': 'Set `cloudFiles.inferColumnTypes` to `true`', 'schema': 'Supply a full schema with `.schema()`',
        'mode': 'Set `schemaEvolutionMode` to `rescue`', 'rename': 'Set `rescuedDataColumn` to a new name'}
  RL = {'rescued': 'In the `_rescued_data` column', 'dropped': 'Nowhere: those rows were dropped', 'bad': 'In the `badRecordsPath` folder',
        'schemas': 'In the `_schemas` folder', 'chk': 'In the stream’s checkpoint'}
  C.append(concept('dea-2-3-schema-hints-rescue', '2', '2.3', 19, 'Auto Loader schema hints and rescued data',
    [{'title': 'Configure schema inference and evolution in Auto Loader', 'url': D + '/ingestion/cloud-object-storage/auto-loader/schema'},
     {'title': 'What is Auto Loader?', 'url': D + '/ingestion/cloud-object-storage/auto-loader/'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'With schema inference and no options set, which type does Auto Loader give the columns of JSON files?', 'answer': '`STRING`, including nested fields', 'why': 'For JSON, CSV and XML, Auto Loader infers strings to avoid type-mismatch problems as the data evolves.'},
      {'id': 'r2', 'type': 'code', 'prompt': 'Make Auto Loader read `amount` and `ts` with fixed types, still inferring the rest.', 'lang': 'python', 'code': '(spark.readStream\n  .format("cloudFiles")\n  .option("cloudFiles.format", "csv")\n  .option("cloudFiles.{{gap}}",\n    "amount double, ts timestamp")\n  .option("cloudFiles.schemaLocation",\n    "/Volumes/fin/chk/payments")\n  .load("/Volumes/fin/raw/payments"))', 'answer': 'schemaHints', 'why': 'Schema hints fix the types you know on top of the inferred schema, and can add a column not yet seen.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'An Auto Loader stream has inferred an `INT` column, then a file holds the text `12a` in it. Where does that value go?', 'answer': 'Into `_rescued_data`', 'why': 'Type mismatches are rescued as a JSON blob with the source file path, instead of being dropped.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Which Auto Loader option makes JSON and CSV schema inference pick real types instead of strings?', 'answer': '`cloudFiles.inferColumnTypes` set to `true`', 'why': 'It switches to the Spark reader’s behavior of choosing types from sample data.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'How much data does Auto Loader sample to infer a schema the first time it reads?', 'answer': 'The first 50 GB or 1,000 files, whichever comes first', 'why': 'It stores the result in `_schemas` under the schema location and tracks changes there.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'An Auto Loader stream infers the schema of partner JSON files. The `discount` field arrives as `5` in some files and `5.5` in others, and finance needs it as a `DOUBLE`. Every other field should stay a string for now.\n\nWhat should the engineer do?', 'pick': 1,
       'correct': [opt(SH['hint'], 'Fixes the type of the column you name and leaves the rest of the inferred schema alone.')],
       'distractors': [opt(SH['infer'], 'Types every column, but the others must stay strings.'),
                       opt(SH['schema'], 'Fixes every column, so nothing else is inferred.'),
                       opt(SH['mode'], 'Controls what happens to new columns, not the type of an existing one.'),
                       opt(SH['rename'], 'Only renames the column where unparsed data goes.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'An Auto Loader stream infers the schema of partner CSV files, and every column arrives as `STRING`. The team wants Auto Loader to choose numeric and date types from the data for all columns, as Spark’s reader does.\n\nWhat should the engineer do?', 'pick': 1,
       'correct': [opt(SH['infer'], 'Makes Auto Loader infer JSON and CSV column types from sample data, as Spark does.')],
       'distractors': [opt(SH['hint'], 'Fixes only the columns you list; the rest stay strings.'),
                       opt(SH['schema'], 'Means writing every type by hand instead of inferring them.'),
                       opt(SH['mode'], 'Governs new columns, not how types are inferred.'),
                       opt(SH['rename'], 'Only renames the rescued data column.')]},
      {'id': 's3', 'stem': 'An Auto Loader stream with an inferred schema loads `quantity` as `INT`. A few files now hold text such as `n/a` in that field, and analysts ask where those original values went.\n\nWhere should they look?', 'pick': 1,
       'correct': [opt(RL['rescued'], 'Type mismatches are rescued there as a JSON blob with the source file path.')],
       'distractors': [opt(RL['dropped'], 'With a rescued data column, type mismatches don’t drop rows.'),
                       opt(RL['bad'], 'Holds only incomplete or malformed records; type mismatches go to the rescued column.'),
                       opt(RL['schemas'], 'That folder tracks the inferred schema over time, not data.'),
                       opt(RL['chk'], 'Holds stream progress and discovered-file metadata, not row values.')]},
    ], setting=['Auto Loader'], rev=1))
  EVIDENCE['dea-2-3-schema-hints-rescue'] = [(0, r'Auto Loader infers all columns as strings \(including nested fields in JSON files\)'),
    (0, r'set the option `cloudFiles\.inferColumnTypes` to `true`'), (0, r'samples the first 50 GB or 1000 files'),
    (0, r'cloudFiles\.schemaHints'), (0, r'use schema hints to add that column'), (0, r'Type mismatches'),
    (0, r'JSON blob with the rescued columns and the source file path'), (0, r'instead of dropping them'),
    (0, r'directory `_schemas` at the configured `cloudFiles\.schemaLocation`'), (0, r'setting the `rescuedDataColumn` option'),
    (0, r'does not treat data type mismatches as bad records when using the `rescuedDataColumn`'),
    (1, r'metadata is persisted in a scalable key-value store \(RocksDB\) in the \*checkpoint location\*')]

  # ---------- 1.1 Delta table history and time travel ----------
  C.append(concept('dea-1-1-delta-history', '1', '1.1', 20, 'Delta table history and time travel',
    [{'title': 'Work with table history', 'url': D + '/tables/history'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'Which command lists every write to a Delta table, with its operation, user and timestamp?', 'answer': '`DESCRIBE HISTORY`', 'why': 'It returns one row per table version, newest first.'},
      {'id': 'r2', 'type': 'code', 'prompt': 'Query a Delta table as it was at version 12.', 'lang': 'sql', 'code': 'SELECT *\nFROM retail.silver.orders\n{{gap}} 12;', 'answer': 'VERSION AS OF', 'why': 'Time travel by version; `TIMESTAMP AS OF` does the same by time, and `orders@v12` is shorthand.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'By default, how far back can a Unity Catalog managed Delta table be queried with time travel?', 'answer': '7 days', 'why': 'Versions older than `deletedFileRetentionDuration` (7 days by default) are blocked, though history is kept longer.'},
      {'id': 'r4', 'type': 'comparison', 'prompt': 'For a Delta table, which default is longer: how long history is kept, or how far back time travel works?', 'answer': 'History: 30 days, against 7 for time travel', 'why': '`logRetentionDuration` keeps history 30 days; `deletedFileRetentionDuration` limits time travel to 7.'},
      {'id': 'r5', 'type': 'symptom', 'prompt': 'A Delta time travel query to a version from three weeks ago fails, though `DESCRIBE HISTORY` still lists it. Likely cause?', 'answer': 'The version is past the 7-day file retention window', 'why': 'History is kept 30 days, but time travel beyond `deletedFileRetentionDuration` is blocked and `VACUUM` may have removed its files.'},
    ], setting=['Delta'], rev=1))
  EVIDENCE['dea-1-1-delta-history'] = [(0, r'Run the `DESCRIBE HISTORY` command to retrieve information including the operations, user, and timestamp'),
    (0, r'reverse chronological order'), (0, r'VERSION AS OF 123'), (0, r'TIMESTAMP AS OF'), (0, r'people10m@v123'),
    (0, r'`logRetentionDuration`, which is 30 days by default'), (0, r'`deletedFileRetentionDuration` table property \(default 7 days\)'),
    (0, r'For Unity Catalog managed tables, this applies to Databricks Runtime 12\.2 and above'), (0, r'Data files are deleted when `VACUUM` runs')]
  return C

def chunk2(concept, opt):
  C = []
  J = D + '/jobs'
  # ---------- 4.1 retries and timeouts ----------
  RT = {'retry': 'A retry policy on the task, with an interval', 'tr': 'A timeout on the task, plus a retry policy', 'alldone': 'A `Run if` of All done on the next task',
        'repair': 'A repair run each time the task fails', 'timeout': 'A timeout on the task, with no retries', 'cont': 'A continuous trigger on the whole job'}
  C.append(concept('dea-4-1-retries-timeouts', '4', '4.1', 21, 'Task retries and timeouts',
    [{'title': 'Configure and edit tasks in Lakeflow Jobs', 'url': J + '/configure-task'}, {'title': 'Run jobs continuously', 'url': J + '/continuous'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In Lakeflow Jobs, does a task on classic compute retry after failing if no retry policy is set?', 'answer': 'No: most configurations don’t retry by default', 'why': 'You add a retry policy per task; serverless jobs auto-optimize retries, and continuous jobs use exponential backoff.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'A Lakeflow Jobs task has a 30-minute timeout and 2 retries. How is the timeout applied?', 'answer': 'To each attempt separately', 'why': 'When both are set, the timeout applies to each retry, so every attempt gets the full 30 minutes.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In a Lakeflow Jobs retry policy, the retry interval is measured from what point?', 'answer': 'The start of the failed run', 'why': 'The interval runs from when the failed attempt started to when the retry starts.'},
      {'id': 'r4', 'type': 'comparison', 'prompt': 'In Lakeflow Jobs, how does a continuous job recover from failure, compared with a task retry policy?', 'answer': 'It retries the whole job, with exponential backoff', 'why': 'Continuous jobs don’t use retry policies; task-level retries can be added with Task retry mode set to On failure.', 'src': 1},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A Lakeflow Jobs task calls a partner API that fails quickly a few times a week and recovers within minutes. On-call staff are tired of rerunning it by hand.\n\nWhat should the engineer configure?', 'pick': 1,
       'correct': [opt(RT['retry'], 'Retries the failed task automatically after a wait, so short outages recover on their own.')],
       'distractors': [opt(RT['alldone'], 'Lets the next task run anyway, but the failed call is never retried.'),
                       opt(RT['repair'], 'That’s the manual rerun they want to stop doing.'),
                       opt(RT['timeout'], 'Ends a slow attempt but never tries again.'),
                       opt(RT['cont'], 'Runs the job back to back all day instead of on its schedule.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A Lakeflow Jobs task sometimes hangs for hours on a stuck source connection, though a fresh attempt usually finishes in ten minutes. The team wants it to give up and try again.\n\nWhat should the engineer configure?', 'pick': 1,
       'correct': [opt(RT['tr'], 'The timeout ends each stuck attempt, and because it applies to every retry, a fresh try follows.')],
       'distractors': [opt(RT['retry'], 'Retries only after a failure, and a hung attempt never fails on its own.'),
                       opt(RT['alldone'], 'Changes when the next task runs; the stuck task keeps hanging.'),
                       opt(RT['repair'], 'Needs someone to notice the hang and act by hand.'),
                       opt(RT['timeout'], 'Stops the stuck attempt but never tries again.')]},
      {'id': 's3', 'stem': 'A Lakeflow Jobs task loads files from an SFTP server that is down for maintenance for about 20 minutes most nights. The job should keep trying until the server is back.\n\nWhat should the engineer configure?', 'pick': 1,
       'correct': [opt(RT['retry'], 'A few retries spaced several minutes apart outlast the 20-minute outage.')],
       'distractors': [opt(RT['alldone'], 'Downstream tasks would run on missing data; the load isn’t retried.'),
                       opt(RT['repair'], 'Requires someone to rerun it every night by hand.'),
                       opt(RT['timeout'], 'Doesn’t help: the task fails fast, and nothing retries it.'),
                       opt(RT['cont'], 'Reruns the whole job nonstop instead of retrying one task.')]},
    ], setting=['Lakeflow Jobs'], rev=1))
  EVIDENCE['dea-4-1-retries-timeouts'] = [(0, r'For most configurations, the default setting does not retry any tasks on task failure'),
    (0, r'Serverless jobs auto-optimize retries by default'), (0, r'between the start of the failed run and the subsequent retry run'),
    (0, r'the timeout applies to each retry'), (0, r'Continuous jobs use an exponential backoff retry policy'),
    (1, r'You cannot use \[retry policies\]'), (1, r'\*\*Task retry mode\*\* to \*\*On failure\*\*')]

  # ---------- 4.1 If/else ----------
  C.append(concept('dea-4-1-if-else', '4', '4.1', 22, 'Branching with the If/else condition task',
    [{'title': 'Add branching logic to a job with the If/else task', 'url': J + '/tasks/if-else'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In Lakeflow Jobs, which task type runs part of the task graph only when a boolean expression is true?', 'answer': 'The If/else condition task', 'why': 'It compares two operands with a boolean operator and runs the true or false branch.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'In a Lakeflow Jobs If/else condition, does `12.0 == 12` evaluate to true?', 'answer': 'No', 'why': '`==` and `!=` compare as strings; `>`, `>=`, `<` and `<=` compare numbers, so `12.0 >= 12` is true.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'What can an operand in a Lakeflow Jobs If/else condition reference?', 'answer': 'Job parameters, task parameters and task values', 'why': 'For example `{{job.parameters.env}}` or `{{tasks.load.values.rows}}`.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Which task value types can a Lakeflow Jobs If/else condition use as an operand?', 'answer': 'Numbers, strings and booleans', 'why': 'Any other type makes the condition fail.'},
    ],
    [
      {'id': 's1', 'stem': 'A Lakeflow Jobs ingestion task sets a task value `new_rows`. The transformation tasks should run only when `new_rows` is above zero, and the job should still succeed when it isn’t.\n\nWhat should the engineer add?', 'pick': 1,
       'correct': [opt('An If/else condition task on `new_rows`', 'Branches on the task value, so the transformations run only on the true branch.')],
       'distractors': [opt('A `Run if` of At least one failed', 'Reacts to task failures, not to a value.'),
                       opt('A For each task over the new rows', 'Loops a task over an input array; it doesn’t branch.'),
                       opt('A Run Job task for the transformations', 'Starts another job whether or not there are new rows.'),
                       opt('A table update trigger on the target', 'Starts runs on table changes; it can’t branch inside this job.')]},
      {'id': 's2', 'stem': 'A Lakeflow Jobs job takes a job parameter `env`. A data-masking task must run only when `env` is `prod`, and be skipped in dev and test.\n\nWhat should the engineer add?', 'pick': 1,
       'correct': [opt('An If/else condition task on the `env` parameter', 'Compares `{{job.parameters.env}}` with `prod` and runs the masking task on the true branch.')],
       'distractors': [opt('A `Run if` of All done on the masking task', 'Runs the masking task in every environment.'),
                       opt('A For each task over the environments', 'Runs the task once per environment instead of choosing one.'),
                       opt('A separate job per environment', 'Duplicates the job instead of branching on the parameter.'),
                       opt('A retry policy on the masking task', 'Controls retries after failure, not whether the task runs.')]},
      {'id': 's3', 'stem': 'A Lakeflow Jobs If/else condition compares the task value `ratio`, set to `12.0`, with `12` using `==`. It takes the false branch, but the engineer expected true.\n\nWhy?', 'pick': 1,
       'correct': [opt('`==` compares the two operands as strings', 'So `12.0` and `12` differ; a numeric operator such as `>=` would compare numbers.')],
       'distractors': [opt('Numeric task values aren’t allowed in operands', 'Numbers, strings and booleans are all allowed.'),
                       opt('Task values are always read as booleans', 'They keep their value; non-numeric types are treated as strings.'),
                       opt('The operand must use job parameter syntax', 'Task values are referenced with `{{tasks.<task>.values.<key>}}`.'),
                       opt('`==` rounds both operands to integers', 'It doesn’t round; it compares the text of each operand.')]},
    ], setting=['Lakeflow Jobs'], rev=1))
  EVIDENCE['dea-4-1-if-else'] = [(0, r'`12\.0 == 12` evaluates to false'), (0, r'`12\.0 >= 12` evaluates to true'),
    (0, r'Only numeric, string, and boolean values are allowed'), (0, r'A job parameter variable, for example `\{\{job\.parameters\.<name>\}\}`'),
    (0, r'A task value, for example `\{\{tasks\.<task_name>\.values\.<value_name>\}\}`'), (0, r'A task parameter variable')]

  # ---------- 4.1 For each ----------
  FE = {'fe8': 'A For each task with concurrency 8', 'fe1': 'A For each task with the default concurrency', 'fe3': 'A For each task with concurrency 3',
        'many': 'One notebook task per table, all parallel', 'ie': 'An If/else task that picks each item in turn', 'rj': 'A Run Job task calling a per-item job'}
  C.append(concept('dea-4-1-for-each', '4', '4.1', 23, 'Looping with the For each task',
    [{'title': 'Use a For each task to run another task in a loop', 'url': J + '/tasks/for-each'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'A Lakeflow Jobs For each task has the inputs `[{"table": "sales"}, {"table": "orders"}]`. How does its nested task refer to each table name?', 'answer': '`{{input.table}}`', 'why': '`{{input}}` is the whole element; `{{input.<key>}}` picks one field from an object.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'What is the default Concurrency of a Lakeflow Jobs For each task?', 'answer': '1: iterations run one at a time', 'why': 'Raise it to run several iterations of the nested task in parallel.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'Can the nested task of a Lakeflow Jobs For each task be another For each task?', 'answer': 'No', 'why': 'The nested task must be one of the standard task types.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Where can a Lakeflow Jobs For each task get its input array?', 'answer': 'A JSON array, a task value or a job parameter', 'why': 'A task value lets an earlier task build the list at run time.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'How many characters fit in the Inputs box of a Lakeflow Jobs For each task?', 'answer': '5,000', 'why': 'For larger inputs, reference a task value, which allows up to 48 KB.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A Lakeflow Jobs job must run the same ingestion notebook for each of 40 source tables, at most 8 at a time. An earlier task produces the list of tables as a task value.\n\nWhat should the engineer build?', 'pick': 1,
       'correct': [opt(FE['fe8'], 'Loops the notebook over the task value, running up to 8 iterations in parallel.')],
       'distractors': [opt(FE['fe1'], 'Runs one table at a time, far slower than the 8 allowed.'),
                       opt(FE['many'], 'Can’t follow a list built at run time, and ignores the limit of 8.'),
                       opt(FE['ie'], 'Branches once on a condition; it doesn’t loop.'),
                       opt(FE['rj'], 'Calls a job once; it doesn’t iterate over a list.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A Lakeflow Jobs job must run the same ingestion notebook for each of 3 regions, and each region must finish before the next one starts.\n\nWhat should the engineer build?', 'pick': 1,
       'correct': [opt(FE['fe1'], 'The default concurrency of 1 runs one iteration at a time, in order.')],
       'distractors': [opt(FE['fe3'], 'Runs all three regions at once, which isn’t allowed here.'),
                       opt(FE['many'], 'Runs the regions in parallel, which isn’t allowed here.'),
                       opt(FE['ie'], 'Branches once on a condition; it doesn’t loop.'),
                       opt(FE['rj'], 'Calls a job once; it doesn’t iterate over the regions.')]},
      {'id': 's3', 'stem': 'A Lakeflow Jobs For each task loops a notebook over source tables. Each iteration now needs both a table name and a target schema.\n\nHow should the inputs be passed?', 'pick': 1,
       'correct': [opt('As objects, read with `{{input.<key>}}`', 'Each element carries both fields, and the nested task reads each one by key.')],
       'distractors': [opt('As two For each tasks, one per field', 'Two loops can’t pair each table with its schema.'),
                       opt('As a nested For each task for schemas', 'A For each task can’t contain another For each task.'),
                       opt('As job parameters reset on every loop', 'Job parameters are set once per run, not per iteration.'),
                       opt('As task values set by the nested task', 'Those are outputs of the iteration, not its inputs.')]},
    ], setting=['For each'], rev=1))
  EVIDENCE['dea-4-1-for-each'] = [(0, r'You cannot add another `For each` task as the nested task'), (0, r'The default value is 1'),
    (0, r'\{\{input\.table\}\}'), (0, r'`\{\{input\.<key>\}\}` to reference individual object fields'), (0, r'limited to 5,000 characters'),
    (0, r'48 KB if you use task value references'), (0, r'JSON formatted arrays, task values, or job parameters')]

  # ---------- 4.2 Run if dependencies ----------
  RI = {k: 'Run if: ' + k for k in ['All succeeded', 'At least one succeeded', 'None failed', 'All done', 'At least one failed', 'All failed']}
  C.append(concept('dea-4-2-run-if', '4', '4.2', 24, 'Run if task dependencies',
    [{'title': 'Configure task dependencies', 'url': J + '/run-if'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'What is the default Run if condition for a Lakeflow Jobs task with dependencies?', 'answer': 'All succeeded', 'why': 'If any dependency fails, the task is marked Upstream failed and doesn’t run.'},
      {'id': 'r2', 'type': 'decision', 'prompt': 'A Lakeflow Jobs cleanup task must run after its upstream tasks finish, whether they succeeded or failed. Which Run if condition?', 'answer': 'All done', 'why': 'It runs once every dependency has run, regardless of outcome.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'A Lakeflow Jobs alert task uses Run if At least one failed, and every upstream task succeeds. What happens to the alert task?', 'answer': 'It’s marked Excluded and skipped', 'why': 'Failure-handling conditions that aren’t met mark the task Excluded rather than failed.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'In Lakeflow Jobs, a task’s Run if is All succeeded and one upstream task fails. How is the task marked?', 'answer': 'Upstream failed', 'why': 'All succeeded, At least one succeeded and None failed mark the task Upstream failed when unmet.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'When Lakeflow Jobs evaluates Run if conditions, how does it treat an upstream task marked Excluded?', 'answer': 'As successful', 'why': 'Upstream failed and Upstream canceled count as failed, not skipped.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A Lakeflow Jobs job loads three regions in parallel. A notification task must run only if any of the three loads fails, and be skipped otherwise.\n\nWhich setting should the notification task use?', 'pick': 1,
       'correct': [opt(RI['At least one failed'], 'Runs when any dependency fails, and is excluded when none do.')],
       'distractors': [opt(RI['All failed'], 'Runs only if all three fail, missing a single failure.'),
                       opt(RI['All done'], 'Runs after every load, including when all succeed.'),
                       opt(RI['None failed'], 'Runs only when no load failed, the opposite of what’s needed.'),
                       opt(RI['All succeeded'], 'The default; it runs only when every load succeeds.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A Lakeflow Jobs job loads three regions in parallel. A cleanup task must run after all three loads in every case, whatever their outcome.\n\nWhich setting should the cleanup task use?', 'pick': 1,
       'correct': [opt(RI['All done'], 'Runs once every dependency has run, regardless of success or failure.')],
       'distractors': [opt(RI['At least one failed'], 'Skips cleanup whenever all loads succeed.'),
                       opt(RI['All succeeded'], 'Skips cleanup whenever any load fails.'),
                       opt(RI['None failed'], 'Skips cleanup whenever a load fails.'),
                       opt(RI['At least one succeeded'], 'Skips cleanup when all three loads fail.')]},
      {'id': 's3', 'stem': 'A Lakeflow Jobs job pulls prices from two redundant vendor feeds in parallel. The pricing task can run as long as either feed succeeded.\n\nWhich setting should the pricing task use?', 'pick': 1,
       'correct': [opt(RI['At least one succeeded'], 'Runs when either feed succeeded, and is marked Upstream failed only if both fail.')],
       'distractors': [opt(RI['All succeeded'], 'Needs both feeds, defeating the redundancy.'),
                       opt(RI['None failed'], 'Won’t run if either feed failed.'),
                       opt(RI['All done'], 'Runs even when both feeds failed and there are no prices.'),
                       opt(RI['At least one failed'], 'Runs only when a feed failed, the wrong trigger.')]},
    ], setting=['Lakeflow Jobs'], rev=1))
  EVIDENCE['dea-4-2-run-if'] = [(0, r'\*\*All succeeded\*\*: All dependencies have run and succeeded\. This is the default setting'),
    (0, r'\*\*All done\*\*: The task is run after all its dependencies have run, regardless of the status'),
    (0, r'\*\*At least one failed\*\*: At least one dependency failed\. The task is marked as `Excluded` if the condition is unmet'),
    (0, r'\*\*At least one succeeded\*\*: At least one dependency has succeeded\. The task is marked as `Upstream failed`'),
    (0, r'\*\*None failed\*\*: None of the dependencies failed'), (0, r'\*\*All failed\*\*: All dependencies have failed'),
    (0, r'Upstream tasks with the `Excluded` result state are treated as successful'), (0, r'are treated as failed, not as skipped')]

  # ---------- 4.2 task values ----------
  C.append(concept('dea-4-2-task-values', '4', '4.2', 25, 'Passing values between tasks',
    [{'title': 'Use task values to pass information between tasks', 'url': J + '/task-values'},
     {'title': 'Add branching logic to a job with the If/else task', 'url': J + '/tasks/if-else'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In a Lakeflow Jobs Python notebook task, publish the row count for later tasks.', 'lang': 'python', 'code': 'n = df.count()\ndbutils.jobs.taskValues.{{gap}}(\n  key="row_count", value=n)', 'answer': 'set', 'why': 'A later notebook reads it with `get`; other tasks use `{{tasks.<task>.values.row_count}}`.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'How does a Lakeflow Jobs If/else or SQL task refer to a task value set by the task `load`?', 'answer': '`{{tasks.load.values.<key>}}`', 'why': 'Dynamic value references work in any task that takes parameters.', 'src': 1},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In Lakeflow Jobs, which tasks can call `dbutils.jobs.taskValues.set()`?', 'answer': 'Python notebook tasks only', 'why': 'It’s a Python function; other task types read values through references instead.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'What may a Lakeflow Jobs task value hold, and how large can it be?', 'answer': 'Valid JSON, at most 48 KiB', 'why': 'Anything that can be expressed as JSON, such as a number, string or list.'},
    ], setting=['Lakeflow Jobs'], rev=1))
  EVIDENCE['dea-4-2-task-values'] = [(0, r'dbutils\.jobs\.taskValues\.set\(\)'), (0, r'can be used only in notebooks with Python selected as the language'),
    (0, r'Only values that can be expressed as valid JSON are permitted'), (0, r'cannot exceed 48 KiB'),
    (1, r'`\{\{tasks\.<task_name>\.values\.<value_name>\}\}`')]

  # ---------- 4.3 schedules ----------
  SC = {'adv': 'An advanced schedule with a time zone', 'simple': 'A simple schedule with an interval', 'fa': 'A file arrival trigger on the source',
        'cont': 'A continuous trigger on the job', 'tu': 'A table update trigger on the source'}
  C.append(concept('dea-4-3-schedules', '4', '4.3', 26, 'Simple and advanced job schedules',
    [{'title': 'Run jobs on a schedule', 'url': J + '/scheduled'}],
    [
      {'id': 'r1', 'type': 'comparison', 'prompt': 'In Lakeflow Jobs, simple or advanced schedule: which lets you set the start time and time zone?', 'answer': 'Advanced', 'why': 'A simple schedule repeats an interval from a time the scheduler picks; advanced sets period, time and time zone.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'Which cron syntax does an advanced Lakeflow Jobs schedule use?', 'answer': 'Quartz cron syntax', 'why': 'Tick Show Cron Syntax to see and edit the schedule as a Quartz expression.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'What is the shortest gap Lakeflow Jobs allows between runs started by a schedule, whatever the cron expression says?', 'answer': '10 seconds', 'why': 'Databricks enforces that minimum regardless of the cron configuration.'},
      {'id': 'r4', 'type': 'symptom', 'prompt': 'An hourly Lakeflow Jobs schedule set to a European time zone skips one run in late March. Likely cause?', 'answer': 'Daylight saving time began', 'why': 'In a zone that observes daylight saving, an hourly job can be skipped or delayed; UTC avoids it.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'A scheduled Lakeflow Jobs run starts four minutes late after a cloud hiccup. Is that expected?', 'answer': 'Yes: the scheduler isn’t built for low latency', 'why': 'Runs can be delayed by several minutes and start as soon as the service is available.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A Lakeflow Jobs job must run at 02:30 Johannesburg time every weekday, before the trading desk opens.\n\nWhich trigger should the job use?', 'pick': 1,
       'correct': [opt(SC['adv'], 'Sets the exact time, weekdays and time zone, with Quartz cron if needed.')],
       'distractors': [opt(SC['simple'], 'Repeats an interval from a time the scheduler chooses, so 02:30 can’t be set.'),
                       opt(SC['fa'], 'Runs when files land, not at a fixed time.'),
                       opt(SC['cont'], 'Runs back to back all day instead of once.'),
                       opt(SC['tu'], 'Runs when a table changes, not at a fixed time.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A Lakeflow Jobs housekeeping job must run every 6 hours. The exact start times don’t matter, and the team wants the least to configure.\n\nWhich trigger should the job use?', 'pick': 1,
       'correct': [opt(SC['simple'], 'An interval of 6 hours is all that’s needed; the scheduler picks the first run time.')],
       'distractors': [opt(SC['adv'], 'Works, but sets times and a time zone that nobody needs.'),
                       opt(SC['fa'], 'Depends on files arriving, not on time.'),
                       opt(SC['cont'], 'Runs back to back instead of every 6 hours.'),
                       opt(SC['tu'], 'Depends on table changes, not on time.')]},
      {'id': 's3', 'stem': 'An hourly Lakeflow Jobs job feeds a billing ledger that must never skip or double up an hour, including when clocks change for daylight saving.\n\nHow should its schedule be set?', 'pick': 1,
       'correct': [opt('An advanced schedule in UTC', 'UTC has no daylight saving changes, so every hour runs exactly once.')],
       'distractors': [opt('An advanced schedule in Europe/Berlin', 'Observes daylight saving, so a run can be skipped or delayed when clocks change.'),
                       opt('A file arrival trigger on the ledger', 'Runs when files land, not every hour.'),
                       opt('A continuous trigger on the job', 'Runs back to back, not once an hour.'),
                       opt('A table update trigger on the source', 'Runs on table changes, not on the clock.')]},
    ], setting=['Lakeflow Jobs'], rev=1))
  EVIDENCE['dea-4-3-schedules'] = [(0, r'You cannot specify the time for the first run for a simple schedule'),
    (0, r'\*\*Advanced\*\*: Specify the period, starting time, and time zone'), (0, r'Quartz Cron Syntax'),
    (0, r'minimum interval of 10 seconds between subsequent runs'), (0, r'time zone that observes daylight saving time or UTC'),
    (0, r'an hourly job is skipped or might appear to be delayed'), (0, r'not intended for low-latency jobs'), (0, r'delayed up to several minutes')]

  # ---------- 4.3 file arrival trigger settings ----------
  C.append(concept('dea-4-3-file-arrival-settings', '4', '4.3', 27, 'Setting up a file arrival trigger',
    [{'title': 'Trigger jobs when new files arrive', 'url': J + '/file-arrival-triggers'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'Which storage can a Lakeflow Jobs file arrival trigger monitor?', 'answer': 'A Unity Catalog volume or external location, or a subpath', 'why': 'The location must be governed by Unity Catalog; the trigger watches its root or a folder under it.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'How often does a Lakeflow Jobs file arrival trigger check for new files?', 'answer': 'About every minute, on a best-effort basis', 'why': 'Checks can slow with the storage’s performance; there’s no extra cost beyond the cloud’s listing charges.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'A Lakeflow Jobs file arrival trigger watches `/Volumes/ops/raw/drop/`. Does a file landing in `drop/2026/11/` start a run?', 'answer': 'Yes: subfolders are checked recursively', 'why': 'The trigger looks for new files in every subdirectory of the configured location.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Which two advanced options control how often a Lakeflow Jobs file arrival trigger starts runs?', 'answer': 'Minimum time between triggers, and wait after last change', 'why': 'Both are in seconds; the second lets a batch of files finish landing before a run starts.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'What does Databricks recommend enabling on an external location that a Lakeflow Jobs file arrival trigger watches?', 'answer': 'File events', 'why': 'Change notifications from the cloud improve performance; volumes on such locations get them by default.'},
    ], setting=['file arrival'], rev=1))
  EVIDENCE['dea-4-3-file-arrival-settings'] = [(0, r'either a volume or an external location configured in Unity Catalog'),
    (0, r'root of a Unity Catalog external location or volume, or a subpath'), (0, r'best effort to check for new files every minute'),
    (0, r'do not incur additional costs other than cloud provider costs'), (0, r'recursively checks for new files in all subdirectories'),
    (0, r'Minimum time between triggers in seconds'), (0, r'Wait after last change in seconds'),
    (0, r'enable the external location for managed file events'), (0, r'Volumes on these external locations get file event support by default')]

  # ---------- 6.1 run history and baselines ----------
  C.append(concept('dea-6-1-run-history', '6', '6.1', 28, 'Reading run history for trends',
    [{'title': 'Monitor Lakeflow Jobs', 'url': J + '/monitor'}, {'title': 'Configure and edit tasks in Lakeflow Jobs', 'url': J + '/configure-task'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In the Lakeflow Jobs Runs tab matrix view, what does the height of a run’s bar show?', 'answer': 'How long the run took', 'why': 'Colour shows status: green succeeded, red unsuccessful, pink skipped, yellow waiting for retry.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'How long does Databricks keep Lakeflow Jobs run history in the Runs tab?', 'answer': '60 days', 'why': 'Run history is kept 60 days for both jobs and pipelines.'},
      {'id': 'r3', 'type': 'decision', 'prompt': 'You need to compare Lakeflow Jobs run durations across every job in the account, with SQL. Where do you look?', 'answer': 'The jobs system tables in `system.lakeflow`', 'why': 'They record job and task runs across the account, and join with billing tables for cost.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'How can a Lakeflow Jobs task warn you when it runs longer than usual, without stopping it?', 'answer': 'A run duration warning threshold', 'why': 'Set the expected completion time under Metric thresholds; passing it triggers an event.', 'src': 1},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A nightly Lakeflow Jobs job has crept from 20 to 45 minutes over three weeks. The engineer wants to see which task grew, run by run.\n\nWhere should they look first?', 'pick': 1,
       'correct': [opt('The matrix view in the job’s Runs tab', 'Shows each run and task with bar heights for duration, across the last 60 days.')],
       'distractors': [opt('The Spark UI of the latest run', 'Shows one run’s stages, not a trend across runs.'),
                       opt('The driver logs of the job cluster', 'Cover one run’s output, not durations over time.'),
                       opt('The SQL warehouse query history', 'Lists SQL queries, not job and task run durations.'),
                       opt('The event log of a pipeline', 'This job isn’t a pipeline, and the log covers one pipeline only.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A platform team wants one SQL query comparing Lakeflow Jobs run durations across every job in the account, including cost.\n\nWhere should they look?', 'pick': 1,
       'correct': [opt('The jobs system tables in `system.lakeflow`', 'Account-wide job and task run records that join with the billing tables.')],
       'distractors': [opt('The matrix view in each job’s Runs tab', 'Shows one job at a time in the UI, not a SQL view of all jobs.'),
                       opt('The Spark UI of each job’s runs', 'Shows stages of one run, with no cost data.'),
                       opt('The driver logs of each job cluster', 'Hold one run’s output, not queryable durations.'),
                       opt('The SQL warehouse query history', 'Lists SQL queries, not job runs.')]},
      {'id': 's3', 'stem': 'A Lakeflow Jobs task normally takes 10 minutes. The team wants an alert whenever a run passes 25 minutes, but the run must keep going.\n\nWhat should they configure?', 'pick': 1,
       'correct': [opt('A run duration warning threshold of 25 minutes', 'Triggers an event when the run passes the expected time, without stopping it.')],
       'distractors': [opt('A 25-minute timeout on the task', 'Stops the run, which they don’t want.'),
                       opt('A retry policy with three retries', 'Acts after a failure, not on a slow run.'),
                       opt('A `Run if` condition on the next task', 'Decides whether a later task runs, not when to warn.'),
                       opt('A continuous trigger on the job', 'Changes when the job runs; it sends no alert.')]},
    ], setting=['Lakeflow Jobs'], rev=1))
  EVIDENCE['dea-6-1-run-history'] = [(0, r'height of the individual job run and task run bars visually indicates the run duration'),
    (0, r'Databricks retains run history for 60 days for both jobs and pipelines'), (0, r'waiting for retry is yellow'),
    (0, r'skipped runs are pink'), (0, r'access to the `system\.lakeflow` schema'), (0, r'join the jobs system tables with billing tables'),
    (1, r'Enter a duration in the \*\*Warning\*\* field to configure the task\'s expected completion time')]

  # ---------- 6.2 repair runs ----------
  C.append(concept('dea-6-2-repair-runs', '6', '6.2', 29, 'Repairing a failed job run',
    [{'title': 'Troubleshoot and repair job failures', 'url': J + '/repair-job-failures'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'A Lakeflow Jobs run fails at the third of five chained tasks. What does a repair run execute?', 'answer': 'The unsuccessful tasks and the tasks that depend on them', 'why': 'Successful tasks aren’t rerun, which saves time and compute.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'Before repairing a Lakeflow Jobs run, you fix the failed task’s notebook path. Which settings does the repair use?', 'answer': 'The current, updated settings', 'why': 'Unsuccessful tasks rerun with the current job and task settings.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'A Lakeflow Jobs task appended half its rows, then failed. Is repairing the run safe?', 'answer': 'Not necessarily: it can duplicate data', 'why': 'A repair reruns the task from the start, and Lakeflow Jobs doesn’t make tasks idempotent.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'A Lakeflow Jobs run used the job cluster `etl_cluster`. Which cluster does the first repair run use?', 'answer': 'A new job cluster, `etl_cluster_v1`', 'why': 'A new cluster keeps the original run’s cluster and settings visible.'},
    ],
    [
      {'id': 's1', 'stem': 'In Lakeflow Jobs, `ingest` and `export` start a job. `clean`, `audit` and `profile` depend on `ingest`, and `publish` depends on `clean`. `clean` fails, and every other task that ran succeeds.\n\nWhich two tasks does a repair run execute?', 'pick': 2,
       'correct': [opt('The `clean` task', 'It failed, so the repair reruns it.'), opt('The `publish` task', 'It depends on `clean`, so it runs once `clean` succeeds.')],
       'distractors': [opt('The `ingest` task', 'It succeeded, so the repair doesn’t rerun it.'),
                       opt('The `export` task', 'It succeeded and doesn’t depend on `clean`.'),
                       opt('The `audit` task', 'It succeeded and doesn’t depend on `clean`.'),
                       opt('The `profile` task', 'It succeeded and doesn’t depend on `clean`.')]},
      {'id': 's2', 'flip': 's3', 'stem': 'A Lakeflow Jobs task failed because a source system was down. The source is back, every other task succeeded, and the failed task writes with `MERGE`, so a rerun is safe.\n\nWhat should the team do?', 'pick': 1,
       'correct': [opt('Repair the run right away', 'Reruns only the failed task and its dependents, skipping what succeeded.')],
       'distractors': [opt('Remove the partial output, then repair', 'Not needed here: a `MERGE` rerun doesn’t duplicate data.'),
                       opt('Start a new run of the whole job', 'Reruns tasks that already succeeded.'),
                       opt('Add a retry policy and wait', 'Applies to future runs; this run has already failed.'),
                       opt('Set Run if to All done downstream', 'Changes future dependencies; it doesn’t finish this run.')]},
      {'id': 's3', 'flip': 's2', 'stem': 'A Lakeflow Jobs task failed because a source system was down. The source is back and every other task succeeded, but the failed task had appended half its rows before failing, and its write isn’t idempotent.\n\nWhat should the team do?', 'pick': 1,
       'correct': [opt('Remove the partial output, then repair', 'A repair reruns the task from the start, so the partial rows must go first.')],
       'distractors': [opt('Repair the run right away', 'Would append the first half again, duplicating data.'),
                       opt('Start a new run of the whole job', 'Reruns everything and still duplicates the partial rows.'),
                       opt('Add a retry policy and wait', 'Applies to future runs; this run has already failed.'),
                       opt('Set Run if to All done downstream', 'Changes future dependencies; it doesn’t fix this run.')]},
    ], setting=['Lakeflow Jobs'], rev=1))
  EVIDENCE['dea-6-2-repair-runs'] = [(0, r'running only the subset of unsuccessful tasks and any dependent tasks'),
    (0, r'successful tasks and any tasks that depend on them are not re-run'), (0, r'Unsuccessful tasks are re-run with the current job and task settings'),
    (0, r'A repair re-runs each unsuccessful task from the beginning'), (0, r're-running it can duplicate that data'), (0, r'my_job_cluster_v1')]

  # ---------- 1.1 control plane and compute plane ----------
  C.append(concept('dea-1-1-architecture', '1', '1.1', 30, 'Control plane and compute plane',
    [{'title': 'High-level architecture', 'url': D + '/getting-started/high-level-architecture'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In the Databricks architecture, where does the control plane, including the web application, run?', 'answer': 'In the Databricks account, not your cloud account', 'why': 'It holds the backend services Databricks manages; your data is processed in the compute plane.'},
      {'id': 'r2', 'type': 'comparison', 'prompt': 'In the Databricks architecture, serverless or classic compute: which runs in your own AWS account?', 'answer': 'Classic compute', 'why': 'Classic resources sit in the classic compute plane in your account; serverless runs in a serverless compute plane in the Databricks account.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In the Databricks architecture, where is a classic workspace’s storage bucket?', 'answer': 'In your AWS account', 'why': 'Classic workspaces have a workspace storage bucket in your account; serverless workspaces use default storage.'},
      {'id': 'r4', 'type': 'cloze', 'text': 'In the Databricks architecture, the {{gap}} plane is where your data is processed.', 'answer': 'compute', 'why': 'The control plane holds Databricks’ backend services and web application.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'In the Databricks architecture, which AWS region does a workspace’s serverless compute plane use?', 'answer': 'The same region as the workspace', 'why': 'Databricks creates it in the region you chose for the workspace.'},
    ], setting=['architecture'], rev=1))
  EVIDENCE['dea-1-1-architecture'] = [(0, r'The control plane is located in the Databricks account, not your cloud account'),
    (0, r'The web application is in the control plane'), (0, r'The \*\*compute plane\*\* is where your data is processed'),
    (0, r'serverless compute resources run in a \*serverless compute plane\* in your Databricks account'),
    (0, r'compute resources are in your AWS account in what is called the \*classic compute plane\*'),
    (0, r'The workspace storage bucket is in your AWS account'), (0, r'same AWS region as your workspace')]
  return C

def chunk3(concept, opt):
  C = []
  B = D + '/dev-tools'
  L = D + '/sql/language-manual'
  # ---------- 5.1 Git folders ----------
  C.append(concept('dea-5-1-git-folders', '5', '5.1', 31, 'Committing and merging from Git folders',
    [{'title': 'Create and manage Git folders', 'url': D + '/repos/git-operations-with-repos'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In a Databricks Git folder, you can’t commit to the protected default branch. How do your changes reach it?', 'answer': 'Commit to a new branch, then open a pull request in your Git provider', 'why': 'The pull request is created and merged in the Git provider’s interface, not in the Git folder.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'What must you add before clicking Commit & Push in a Databricks Git folder?', 'answer': 'A commit message', 'why': 'The message is required; Commit & Push then pushes the changes to the remote repository.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In a Databricks Git folder, you switch branches with uncommitted edits that don’t conflict. What happens to them?', 'answer': 'They carry over as uncommitted changes on the new branch', 'why': 'Discard them before or after switching if you don’t want them to follow you.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'From a Databricks Git folder, are notebook outputs committed when notebooks are saved as `.py` source files?', 'answer': 'No, not by default', 'why': 'Outputs are left out of source-format commits; the IPYNB format can include them.'},
    ], setting=['Git folder'], rev=1))
  EVIDENCE['dea-5-1-git-folders'] = [(0, r'Add a required commit message for the changes, and click \*\*Commit & Push\*\*'),
    (0, r'create a new branch and use your Git provider\'s interface to create a pull request and merge it into the default branch'),
    (0, r'Uncommitted changes on the current branch carry over and show as uncommitted changes on the new branch'),
    (0, r'Notebook outputs aren\'t included in commits by default when notebooks are saved in source file formats')]

  # ---------- 5.3 deployment modes ----------
  MD = {'dev': '`mode: development` on the target', 'prod': '`mode: production` on the target', 'force': 'The `--force` flag on every deploy',
        'unpause': '`pause_status: UNPAUSED` on that job', 'conc': '`max_concurrent_runs: 1` on the job', 'cid': 'The `--cluster-id` flag on deploy'}
  C.append(concept('dea-5-3-deployment-modes', '5', '5.3', 32, 'Bundle deployment modes',
    [{'title': 'Declarative Automation Bundles deployment modes', 'url': B + '/bundles/deployment-modes'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In a Declarative Automation Bundle, make this target prefix deployed jobs with your name and pause their schedules.', 'lang': 'yaml', 'code': 'targets:\n  dev:\n    mode: {{gap}}\n    default: true', 'answer': 'development', 'why': 'Development mode prefixes resources with `[dev <short name>]`, tags them `dev` and pauses schedules and triggers.'},
      {'id': 'r2', 'type': 'symptom', 'prompt': 'After `databricks bundle deploy -t dev`, a Declarative Automation Bundle job’s schedule never fires. The target uses development mode. Why?', 'answer': 'Development mode pauses all schedules and triggers', 'why': 'Set that job’s `pause_status` to `UNPAUSED` to let it run.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In production mode, what does a Declarative Automation Bundle deploy check about Git?', 'answer': 'That the current branch matches the target’s `git.branch`', 'why': 'The check applies when the target names a branch, and `--force` overrides it.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Which identity does Databricks recommend for production deployments of a Declarative Automation Bundle?', 'answer': 'A service principal, set with `run_as`', 'why': 'Production mode also checks that `run_as` and `permissions` are specified.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'In a Declarative Automation Bundle, what happens to deployed Lakeflow Declarative Pipelines in development mode?', 'answer': 'They’re marked `development: true`', 'why': 'Production mode checks the opposite: every related pipeline must be `development: false`.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'Several engineers deploy the same Declarative Automation Bundle into one shared dev workspace. Their copies must not overwrite each other, and no schedule may fire while they iterate.\n\nWhat should the dev target set?', 'pick': 1,
       'correct': [opt(MD['dev'], 'Prefixes each engineer’s resources with their name and pauses every schedule and trigger.')],
       'distractors': [opt(MD['prod'], 'Adds production checks; it doesn’t prefix resources or pause schedules.'),
                       opt(MD['force'], 'Only overrides the Git branch check in production mode.'),
                       opt(MD['conc'], 'Limits concurrent runs; copies would still collide by name.'),
                       opt(MD['cid'], 'Swaps the cluster used, not the resource names or schedules.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A Declarative Automation Bundle’s prod target must deploy only from the `main` branch, with no pipeline left in development mode and permissions stated explicitly.\n\nWhat should the prod target set?', 'pick': 1,
       'correct': [opt(MD['prod'], 'Validates the Git branch, `development: false` on pipelines, and that `run_as` and `permissions` are set.')],
       'distractors': [opt(MD['dev'], 'Marks pipelines as development and pauses schedules, the opposite of what prod needs.'),
                       opt(MD['force'], 'Skips the branch check that prod relies on.'),
                       opt(MD['conc'], 'Affects concurrent runs, not branch or permission checks.'),
                       opt(MD['cid'], 'Not allowed in production mode, and unrelated to these checks.')]},
      {'id': 's3', 'stem': 'A Declarative Automation Bundle is deployed in development mode for a week-long test. One job’s schedule must actually run during the test; the rest stay paused.\n\nWhat should the engineer set?', 'pick': 1,
       'correct': [opt(MD['unpause'], 'Unpauses just that job; development mode still pauses the others.')],
       'distractors': [opt(MD['prod'], 'Turns off every development behavior, not just the one pause.'),
                       opt(MD['force'], 'Overrides the Git branch check, not schedules.'),
                       opt(MD['conc'], 'Turns off concurrent runs; the schedule stays paused.'),
                       opt(MD['cid'], 'Overrides the cluster; the schedule stays paused.')]},
    ], setting=['Declarative Automation Bundle'], rev=1))
  EVIDENCE['dea-5-3-deployment-modes'] = [(0, r'prefix `\[dev \$\{workspace\.current_user\.short_name\}\]`'), (0, r'Pauses all schedules and triggers'),
    (0, r'Marks all related deployed Lakeflow pipelines as `development: true`'), (0, r'set the `pause_status` to `UNPAUSED`'),
    (0, r'setting `max_concurrent_runs` to `1`'), (0, r'Enables the use of `--cluster-id <cluster-id>`'),
    (0, r'Validates that all related deployed Lakeflow pipelines are marked as `development: false`'),
    (0, r'Validates that the current Git branch is equal to the Git branch that is specified in the target'),
    (0, r'This validation can be overridden by specifying `--force`'), (0, r'recommends that you use service principals for production deployments'),
    (0, r'Validates that the `run_as` and `permissions` mappings are specified'),
    (0, r'does not allow overriding any existing cluster definitions')]

  # ---------- 5.4 bundle CLI commands ----------
  CL = {k: '`databricks bundle ' + k + '`' for k in ['validate', 'deploy', 'run', 'destroy', 'init', 'summary']}
  C.append(concept('dea-5-4-bundle-cli', '5', '5.4', 33, 'Bundle commands in the Databricks CLI',
    [{'title': 'bundle command group', 'url': B + '/cli/bundle-commands'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'Which Databricks CLI command checks that a bundle’s configuration files are syntactically correct, without deploying?', 'answer': '`databricks bundle validate`', 'why': 'Run it first in CI so configuration errors fail fast.'},
      {'id': 'r2', 'type': 'code', 'prompt': 'With the Databricks CLI, deploy the bundle to its `prod` target.', 'lang': 'bash', 'code': 'databricks bundle deploy {{gap}} prod', 'answer': '-t', 'why': '`-t` or `--target` picks the target; without it, the default target is used.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'Which target does Databricks CLI `bundle deploy` use when you name none?', 'answer': 'The default target in the bundle configuration', 'why': 'Mark one target `default: true`, usually dev.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Which Databricks CLI bundle command permanently deletes the jobs, pipelines and artifacts a bundle deployed?', 'answer': '`databricks bundle destroy`', 'why': 'It can’t be undone.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'Which Databricks CLI bundle command starts a job or pipeline defined in the bundle?', 'answer': '`databricks bundle run`', 'why': 'Give the resource key, or it prompts you to choose one.'},
    ],
    [
      {'id': 's1', 'stem': 'A CI workflow must catch bundle configuration errors on every pull request, then put the bundle into production after merge. It uses the Databricks CLI.\n\nWhich two commands does it need?', 'pick': 2,
       'correct': [opt(CL['validate'], 'Checks the configuration files on each pull request without deploying.'),
                   opt(CL['deploy'], 'With `-t prod`, deploys the merged bundle to the production target.')],
       'distractors': [opt(CL['init'], 'Creates a new bundle from a template; CI doesn’t need it.'),
                       opt(CL['destroy'], 'Deletes deployed resources, the opposite of releasing them.'),
                       opt(CL['run'], 'Starts a deployed job or pipeline; it doesn’t check or deploy.'),
                       opt(CL['summary'], 'Describes a deployment; it doesn’t check or deploy.')]},
      {'id': 's2', 'stem': 'A Databricks CLI step in CI has just deployed a bundle to staging. The next step must start the bundle’s integration-test job.\n\nWhich command should it use?', 'pick': 1,
       'correct': [opt(CL['run'], 'Runs the job by its key in the bundle.')],
       'distractors': [opt(CL['deploy'], 'Already done; it deploys but doesn’t start the job.'),
                       opt(CL['validate'], 'Checks configuration; it doesn’t run anything.'),
                       opt(CL['init'], 'Creates a new bundle from a template.'),
                       opt(CL['destroy'], 'Deletes what was just deployed.')]},
      {'id': 's3', 'stem': 'A feature branch’s bundle was deployed to a shared test workspace with the Databricks CLI. The branch is abandoned, and its jobs and pipelines must be removed.\n\nWhich command should the engineer run?', 'pick': 1,
       'correct': [opt(CL['destroy'], 'Permanently deletes the jobs, pipelines and artifacts that bundle deployed.')],
       'distractors': [opt(CL['deploy'], 'Would deploy them again, not remove them.'),
                       opt(CL['validate'], 'Checks configuration; it removes nothing.'),
                       opt(CL['run'], 'Starts a job; it removes nothing.'),
                       opt(CL['summary'], 'Describes the deployment; it removes nothing.')]},
    ], setting=['Databricks CLI'], rev=1))
  EVIDENCE['dea-5-4-bundle-cli'] = [(0, r'Validate bundle configuration files are syntactically correct'), (0, r'set the `-t` \(or `--target`\) option'),
    (0, r'the default target as declared within the bundle configuration files is used'),
    (0, r'permanently deletes a bundle\'s previously-deployed jobs, pipelines, and artifacts\. This action cannot be undone'),
    (0, r'Run a job, pipeline, app, or script'), (0, r'Initialize a new bundle using a bundle template'), (0, r'## databricks bundle summary')]

  # ---------- 5.4 CI/CD identity and authentication ----------
  C.append(concept('dea-5-4-cicd-auth', '5', '5.4', 34, 'CI/CD identity and authentication',
    [{'title': 'CI/CD on Databricks', 'url': B + '/ci-cd'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'What does Databricks recommend as the approach to CI/CD on Databricks?', 'answer': 'Declarative Automation Bundles', 'why': 'They describe jobs, pipelines and other resources as source files that deploy to each environment.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'Which kind of identity should a Databricks CI/CD pipeline authenticate as?', 'answer': 'A service principal, not a user', 'why': 'Deployments then don’t depend on any one person’s account or credentials.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'Which Databricks CI/CD authentication method needs no Databricks secrets stored in the CI system?', 'answer': 'Workload identity federation (OAuth token federation)', 'why': 'Databricks calls it the most secure way for CI/CD to authenticate.'},
    ],
    [
      {'id': 's1', 'stem': 'A GitHub Actions CI/CD workflow deploys bundles to Databricks. Security forbids storing any long-lived Databricks secret in GitHub.\n\nHow should the workflow authenticate?', 'pick': 1,
       'correct': [opt('Workload identity federation for a service principal', 'Exchanges the CI system’s own token for Databricks access, so no Databricks secret is stored.')],
       'distractors': [opt('An OAuth secret for a service principal', 'Works, but it’s a long-lived Databricks secret stored in GitHub.'),
                       opt('A lead engineer’s personal access token', 'A long-lived secret tied to one person.'),
                       opt('The engineer’s own browser OAuth login', 'Needs a person to sign in, so CI can’t run unattended.'),
                       opt('A token kept in a Databricks secret scope', 'GitHub would still need a credential to read it.')]},
      {'id': 's2', 'stem': 'A CI/CD workflow deploys bundles with one developer’s personal access token. Deployments broke when that developer left the company.\n\nWhat should the team change?', 'pick': 1,
       'correct': [opt('Run deployments as a service principal', 'A non-human identity that doesn’t leave, as Databricks recommends for CI/CD.')],
       'distractors': [opt('Use another developer’s personal token', 'Moves the same risk to the next person.'),
                       opt('Rotate the developer’s token every month', 'The token still belongs to a person.'),
                       opt('Run deployments as a workspace admin user', 'Still a person, now with broader rights.'),
                       opt('Share one personal token across the team', 'Still a person’s token, and harder to audit.')]},
      {'id': 's3', 'stem': 'A team wants its jobs and pipelines defined as source files, reviewed in pull requests and promoted by CI/CD from dev to test to prod.\n\nWhat does Databricks recommend?', 'pick': 1,
       'correct': [opt('Declarative Automation Bundles', 'Define the resources as source and deploy them to each target from CI/CD.')],
       'distractors': [opt('Git folders on their own', 'Version notebook code, but don’t deploy jobs and pipelines per environment.'),
                       opt('Exports from the Workspace API', 'Copies files, not job and pipeline definitions per target.'),
                       opt('Hand edits in each Jobs UI', 'Unreviewed and impossible to promote consistently.'),
                       opt('Notebook copies in each workspace', 'Drift between environments, with no definitions as source.')]},
    ], setting=['CI/CD'], rev=1))
  EVIDENCE['dea-5-4-cicd-auth'] = [(0, r'are the recommended approach to CI/CD on Databricks'), (0, r'Use service principals, instead of users, with CI/CD'),
    (0, r'Use workload identity federation for CI/CD authentication, which eliminates the need for Databricks secrets, making it the most secure way')]

  # ---------- 6.4 liquid clustering ----------
  LC = {'auto': 'Automatic liquid clustering, `CLUSTER BY AUTO`', 'keys': 'Liquid clustering on the filter columns', 'part': 'Partitioning by the most-filtered column',
        'z': 'Z-ordering on the current filter columns', 'mv': 'A materialized view per query pattern'}
  C.append(concept('dea-6-4-liquid-clustering', '6', '6.4', 35, 'Liquid clustering',
    [{'title': 'Use liquid clustering for tables', 'url': D + '/tables/clustering'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'Create a Delta table with liquid clustering on `user_id` and `event_ts`.', 'lang': 'sql', 'code': 'CREATE TABLE web.silver.events (\n  event_ts TIMESTAMP,\n  user_id BIGINT,\n  page STRING)\n{{gap}} (user_id, event_ts);', 'answer': 'CLUSTER BY', 'why': 'Liquid clustering keys go in `CLUSTER BY`; it replaces partitioning and `ZORDER`.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'Can liquid clustering be combined with partitioning or `ZORDER` on the same table?', 'answer': 'No', 'why': 'Clustering is not compatible with either; it replaces both.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'You change a table’s liquid clustering keys. Is existing data rewritten?', 'answer': 'No; `OPTIMIZE ... FULL` reclusters it if needed', 'why': 'Keys can be redefined without rewriting data, unlike partitioning.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Which liquid clustering option lets Databricks pick the keys from query patterns, and on which tables?', 'answer': '`CLUSTER BY AUTO`, on Unity Catalog managed tables', 'why': 'Predictive optimization chooses and adapts the keys over time.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'In Databricks Runtime 18.1 and above, how do you move a partitioned Delta table to liquid clustering?', 'answer': '`ALTER TABLE ... REPLACE PARTITIONED BY WITH CLUSTER BY`', 'why': 'It converts in place, with little reader or writer downtime, for managed and external tables.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A Unity Catalog managed table is filtered by different columns as analysts’ needs change. The team wants a better data layout but doesn’t want to choose or maintain keys.\n\nWhat should the engineer use?', 'pick': 1,
       'correct': [opt(LC['auto'], 'Predictive optimization picks and adapts the clustering keys from query patterns.')],
       'distractors': [opt(LC['keys'], 'Works, but someone must choose and maintain the keys.'),
                       opt(LC['part'], 'Rigid, hard to change, and helps only one column.'),
                       opt(LC['z'], 'Must be rerun and re-chosen as the filters change.'),
                       opt(LC['mv'], 'Multiplies storage and still leaves the base layout unchanged.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'An external Delta table is almost always filtered by `customer_id` and `order_date`. The team wants a better data layout.\n\nWhat should the engineer use?', 'pick': 1,
       'correct': [opt(LC['keys'], 'Clusters on the known filter columns; automatic clustering is only for managed tables.')],
       'distractors': [opt(LC['auto'], 'Only available for Unity Catalog managed tables, and this one is external.'),
                       opt(LC['part'], 'Rigid, and can’t serve two filter columns well.'),
                       opt(LC['z'], 'Older technique that liquid clustering replaces.'),
                       opt(LC['mv'], 'Adds a copy instead of fixing the table’s layout.')]},
      {'id': 's3', 'stem': 'A Delta table partitioned by `sale_date` has thousands of tiny partitions, and queries filter by date and store. The team runs Databricks Runtime 18.1 and wants a better data layout with little downtime.\n\nWhat should the engineer do?', 'pick': 1,
       'correct': [opt('Convert with `REPLACE PARTITIONED BY WITH CLUSTER BY`', 'Turns the partitioned table into a liquid clustered one in place.')],
       'distractors': [opt('Add `ZORDER` on store within each partition', 'Keeps the over-partitioning that causes the problem.'),
                       opt('Also partition by `store_id`', 'Creates even more, even smaller partitions.'),
                       opt('Add `CLUSTER BY` next to the partitions', 'Liquid clustering isn’t compatible with partitioning.'),
                       opt('Run `OPTIMIZE` nightly on each partition', 'Compacts files but keeps the partition layout.')]},
    ], setting=['liquid clustering', 'data layout'], rev=1))
  EVIDENCE['dea-6-4-liquid-clustering'] = [(0, r'replaces table partitioning and `ZORDER`'), (0, r'redefine clustering keys without rewriting existing data'),
    (0, r'Clustering is not compatible with partitioning or `ZORDER`'), (0, r'Only available for Unity Catalog managed tables'),
    (0, r'lets predictive optimization adapt over time'), (0, r'OPTIMIZE <table_name> FULL'), (0, r'Databricks Runtime 18\.1 and above, to convert an existing partitioned Delta Lake table'),
    (0, r'supports both external and managed tables'), (0, r'CLUSTER BY \(')]

  # ---------- 6.5 executor memory failures ----------
  MM = {'mem': 'Switch to 4-core, 32 GB workers and rerun', 'cores': 'Switch to 8-core, 32 GB workers and rerun', 'more': 'Add more workers of the same type',
        'retry': 'Raise the task retry count', 'fewer': 'Lower `spark.sql.shuffle.partitions`'}
  C.append(concept('dea-6-5-memory-failures', '6', '6.5', 36, 'Diagnosing Spark memory failures',
    [{'title': 'Spark memory issues', 'url': D + '/optimizations/spark-ui-guide/spark-memory-issues'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'A Spark job fails with `ExecutorLostFailure`, and the event log shows no spot losses or autoscaling. How do you confirm it’s a memory problem?', 'answer': 'Double the memory per core and see if it stops failing', 'why': 'If more memory fixes it, keep the larger workers or look for the cause.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'When testing a Spark memory problem, which matters: total cluster memory or memory per core?', 'answer': 'Memory per core', 'why': 'Going from 4 GB to 8 GB per core tests the hypothesis; adding cores at the same ratio doesn’t.'},
      {'id': 'r3', 'type': 'symptom', 'prompt': 'A Spark window function with no `PARTITION BY` runs out of memory. Why?', 'answer': 'The window spans the whole dataset', 'why': 'Add `PARTITION BY` so each window covers only part of the data.'},
      {'id': 'r4', 'type': 'symptom', 'prompt': 'A Spark job applying a Python UDF runs out of executor memory. Likely cause?', 'answer': 'Each UDF task may load its whole partition into memory', 'why': 'Rewrite it with native functions, or repartition before applying it.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'Which Spark setting does Databricks suggest when too few shuffle partitions cause memory errors?', 'answer': '`spark.sql.shuffle.partitions` set to `auto`', 'why': 'Spark then picks the number of shuffle partitions itself.'},
    ],
    [
      {'id': 's1', 'stem': 'A Spark job’s executors keep being removed, and its stage fails after 4 attempts. The event log shows no spot losses or autoscaling. Workers have 4 cores and 16 GB.\n\nWhat’s the quickest way to confirm a memory problem?', 'pick': 1,
       'correct': [opt(MM['mem'], 'Doubles memory per core from 4 GB to 8 GB, which tests the memory hypothesis.')],
       'distractors': [opt(MM['cores'], 'Still 4 GB per core; the ratio, not the total, matters.'),
                       opt(MM['more'], 'Same memory per core, so each task faces the same limit.'),
                       opt(MM['retry'], 'Retries the same failing tasks; it tests nothing.'),
                       opt(MM['fewer'], 'Makes partitions bigger, adding memory pressure.')]},
      {'id': 's2', 'stem': 'A Spark job runs out of memory in a join. One side is a 40 GB table that carries a broadcast hint.\n\nWhat should the engineer change first?', 'pick': 1,
       'correct': [opt('Remove the broadcast hint on the large table', 'A large broadcast is a common memory cause; let Spark shuffle-join it instead.')],
       'distractors': [opt('Broadcast the other side as well', 'Adds a second broadcast to the memory load.'),
                       opt('Rewrite the join as a Python UDF', 'UDFs can load whole partitions into memory, making it worse.'),
                       opt(MM['fewer'], 'Bigger partitions add memory pressure.'),
                       opt(MM['retry'], 'Retries hit the same broadcast.')]},
      {'id': 's3', 'stem': 'A Spark query uses `ROW_NUMBER() OVER (ORDER BY ts)` across a large table. It runs as one long task and then runs out of memory.\n\nWhat should the engineer change?', 'pick': 1,
       'correct': [opt('Add `PARTITION BY` to the window', 'Splits the window so it doesn’t span the whole dataset in one task.')],
       'distractors': [opt('Set `spark.sql.shuffle.partitions` to `auto`', 'The unpartitioned window still runs in one task.'),
                       opt(MM['more'], 'One task still holds the whole dataset.'),
                       opt('Rewrite the window as a Python UDF', 'UDFs add memory pressure rather than splitting the work.'),
                       opt(MM['retry'], 'Retries hit the same single task.')]},
    ], setting=['Spark'], rev=1))
  EVIDENCE['dea-6-5-memory-failures'] = [(0, r'ExecutorLostFailure'), (0, r'verify it by doubling the memory per core'),
    (0, r'The ratio of memory to cores matters, not the total memory'), (0, r'Set `spark\.sql\.shuffle\.partitions` to `auto`'),
    (0, r'Check for broadcast join hints on large tables'), (0, r'might load all the data in its partition into memory'),
    (0, r'Add a `PARTITION BY` clause so that the'), (0, r'compute\'s event log doesn\'t show spot or preemptible instance losses or autoscaling')]

  # ---------- 3.1 cleaning bronze values ----------
  C.append(concept('dea-3-1-clean-values', '3', '3.1', 37, 'Cleaning bad types and nulls',
    [{'title': 'try_cast function', 'url': L + '/functions/try_cast'}, {'title': 'coalesce function', 'url': L + '/functions/coalesce'},
     {'title': 'PySpark basics', 'url': D + '/pyspark/basics'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In Databricks SQL, cast bronze `amount` strings to decimals, turning malformed values into NULL instead of failing.', 'lang': 'sql', 'code': 'SELECT order_id,\n  {{gap}}(amount AS DECIMAL(10,2))\n    AS amount\nFROM shop.bronze.orders;', 'answer': 'try_cast', 'why': 'A malformed or out-of-range value gives NULL instead of an error.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'In Databricks SQL, what does `try_cast(\'12x\' AS INT)` return?', 'answer': 'NULL', 'why': 'The value isn’t well formed, so `try_cast` returns NULL where `cast` would raise an error.'},
      {'id': 'r3', 'type': 'code', 'prompt': 'In Databricks SQL, replace a missing `country` with `unknown` while cleaning bronze data.', 'lang': 'sql', 'code': "SELECT customer_id,\n  {{gap}}(country, 'unknown')\n    AS country\nFROM crm.bronze.customers;", 'answer': 'coalesce', 'why': 'It returns the first non-null argument, reading left to right.', 'src': 1},
      {'id': 'r4', 'type': 'code', 'prompt': 'In PySpark, drop only the rows where every column is null.', 'lang': 'python', 'code': 'leads = spark.table("crm.bronze.leads")\nclean = leads.na.drop("{{gap}}")', 'answer': 'all', 'why': '`any`, the alternative, drops a row with at least one null.', 'src': 2},
      {'id': 'r5', 'type': 'comparison', 'prompt': 'In Databricks SQL, `cast` or `try_cast`: which raises an error when a value isn’t well formed?', 'answer': '`cast`', 'why': '`try_cast` returns NULL instead of an invalid data error.'},
    ], setting=['SQL', 'PySpark'], rev=1))
  EVIDENCE['dea-3-1-clean-values'] = [(0, r'the result is `NULL` instead of an invalid data error'), (0, r'the result is `NULL` instead of an overflow error'),
    (1, r'Returns the first non-null argument'), (2, r'drop rows containing `any` null values or `all` null values'), (2, r'na\.drop\("all"\)')]

  # ---------- 3.2 UNION and UNION ALL ----------
  SO = {k: 'The `' + k + '` operator' for k in ['UNION ALL', 'UNION', 'UNION DISTINCT', 'INTERSECT', 'EXCEPT']}
  C.append(concept('dea-3-2-union', '3', '3.2', 38, 'UNION, UNION ALL and other set operators',
    [{'title': 'Set operators', 'url': L + '/sql-ref-syntax-qry-select-setops'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In Databricks SQL, does `UNION` keep duplicate rows?', 'answer': 'No: `UNION` means `UNION DISTINCT`', 'why': 'Use `UNION ALL` to keep duplicates.'},
      {'id': 'r2', 'type': 'code', 'prompt': 'In Databricks SQL, stack two order tables, keeping every row even when two are identical.', 'lang': 'sql', 'code': 'SELECT * FROM shop.silver.web_orders\nUNION {{gap}}\nSELECT * FROM shop.silver.app_orders;', 'answer': 'ALL', 'why': '`UNION ALL` preserves duplicates; plain `UNION` removes them.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In Databricks SQL, what is the default for `INTERSECT` and `EXCEPT`: `ALL` or `DISTINCT`?', 'answer': '`DISTINCT`', 'why': 'As with `UNION`, duplicates are removed unless `ALL` is written.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'In Databricks SQL, two duplicate-free queries return 3 and 2 rows, and one row appears in both. How many rows do `UNION` and `UNION ALL` return?', 'answer': '4 and 5', 'why': '`UNION` drops the shared row once; `UNION ALL` keeps it twice.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'In Databricks SQL, daily web and app order events are stacked into one silver table. The same event row can legitimately appear in both feeds, and every row must be counted.\n\nWhich operator fits?', 'pick': 1,
       'correct': [opt(SO['UNION ALL'], 'Keeps every row, including identical ones.')],
       'distractors': [opt(SO['UNION'], 'Removes identical rows, losing legitimate events.'),
                       opt(SO['UNION DISTINCT'], 'Same as `UNION`: identical rows are removed.'),
                       opt(SO['INTERSECT'], 'Keeps only rows found in both feeds.'),
                       opt(SO['EXCEPT'], 'Keeps web rows that aren’t in the app feed.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'In Databricks SQL, two vendors’ customer lists are combined for a mailing. A customer listed identically by both vendors must appear only once.\n\nWhich operator fits?', 'pick': 1,
       'correct': [opt(SO['UNION'], 'Combines both lists and removes identical rows, since `DISTINCT` is the default.')],
       'distractors': [opt(SO['UNION ALL'], 'Keeps both copies of a shared customer.'),
                       opt(SO['INTERSECT'], 'Keeps only customers on both lists.'),
                       opt(SO['EXCEPT'], 'Keeps one vendor’s customers missing from the other.'),
                       opt('The `INTERSECT ALL` operator', 'Keeps only shared customers, with repeats.')]},
      {'id': 's3', 'stem': 'In Databricks SQL, a silver table must list customers in the CRM extract who are missing from the billing extract. Both extracts have the same columns.\n\nWhich operator fits?', 'pick': 1,
       'correct': [opt(SO['EXCEPT'], 'Returns CRM rows with no match in billing.')],
       'distractors': [opt(SO['UNION'], 'Combines both lists instead of finding what’s missing.'),
                       opt(SO['UNION ALL'], 'Combines both lists, duplicates included.'),
                       opt(SO['INTERSECT'], 'Returns customers found in both extracts.'),
                       opt(SO['UNION DISTINCT'], 'Combines both lists without duplicates.')]},
    ], setting=['SQL'], rev=1))
  EVIDENCE['dea-3-2-union'] = [(0, r'If `ALL` is specified duplicate rows are preserved'), (0, r'If `DISTINCT` is specified the result does not contain any duplicate rows\. This is the default'),
    (0, r'\*\*INTERSECT \[ALL \| DISTINCT\]\*\*'), (0, r'\*\*EXCEPT \[ALL \| DISTINCT \]\*\*')]

  # ---------- 3.3 explode and split ----------
  C.append(concept('dea-3-3-explode-split', '3', '3.3', 39, 'Exploding arrays and splitting strings',
    [{'title': 'explode table-valued generator function', 'url': L + '/functions/explode'},
     {'title': 'explode_outer table-valued generator function', 'url': L + '/functions/explode_outer'},
     {'title': 'split function', 'url': L + '/functions/split'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In Databricks SQL, give each element of the `items` array its own row, keeping orders whose array is NULL.', 'lang': 'sql', 'code': 'SELECT order_id,\n  {{gap}}(items) AS item\nFROM shop.bronze.orders;', 'answer': 'explode_outer', 'why': 'For a NULL array it returns one row with a NULL item; `explode` returns none.', 'src': 1},
      {'id': 'r2', 'type': 'basic', 'prompt': 'In Databricks SQL, what does `explode` produce for a row whose array is NULL?', 'answer': 'No rows', 'why': 'The row disappears from the result; `explode_outer` keeps it with a NULL.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In Databricks SQL, can one `SELECT` list hold two generator functions such as `explode`?', 'answer': 'No: it raises `UNSUPPORTED_GENERATOR.MULTI_GENERATOR`', 'why': 'Only one generator is allowed per `SELECT` list.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'In Databricks SQL, what does `split(\'a,b,c\', \',\', 2)` return?', 'answer': '`["a", "b,c"]`', 'why': 'With a limit above 0, the last element holds everything after the last split.', 'src': 2},
      {'id': 'r5', 'type': 'code', 'prompt': 'In Databricks SQL, turn a comma-separated `tags` string into an array.', 'lang': 'sql', 'code': "SELECT post_id,\n  {{gap}}(tags, ',') AS tag_list\nFROM blog.bronze.posts;", 'answer': 'split', 'why': 'It splits around matches of a regular expression and returns an array.', 'src': 2},
    ], setting=['SQL'], rev=1))
  EVIDENCE['dea-3-3-explode-split'] = [(0, r'If `collection` is `NULL` no rows are produced'), (0, r'UNSUPPORTED\\_GENERATOR\.MULTI\\_GENERATOR'),
    (1, r'If `collection` is `NULL` a single row with `NULL`s for the array or map values is produced'),
    (2, r'resulting array\'s last entry will contain all input beyond the last matched `regex`'), (2, r'Splits `str` around occurrences that match `regex` and returns an array')]

  # ---------- 3.4 approximate distinct counts ----------
  AC = {'approx': '`approx_count_distinct(id)`', 'exact': '`count(DISTINCT id)`', 'sumd': '`sum(DISTINCT id)`',
        'tight': '`approx_count_distinct(id, 0.01)`', 'loose': '`approx_count_distinct(id, 0.1)`'}
  C.append(concept('dea-3-4-approx-distinct', '3', '3.4', 40, 'Exact or approximate distinct counts',
    [{'title': 'approx_count_distinct aggregate function', 'url': L + '/functions/approx_count_distinct'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In Databricks SQL, what does `approx_count_distinct` give up for speed, and how much by default?', 'answer': 'Exactness: results within about 5%', 'why': 'The default comes from its `relativeSD` argument.'},
      {'id': 'r2', 'type': 'code', 'prompt': 'In Databricks SQL, estimate distinct users per page cheaply over billions of rows.', 'lang': 'sql', 'code': 'SELECT page,\n  {{gap}}(user_id)\n    AS approx_users\nFROM web.gold.page_views\nGROUP BY page;', 'answer': 'approx_count_distinct', 'why': 'It estimates distinct values per group instead of counting them exactly.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In Databricks SQL, which argument of `approx_count_distinct` sets the allowed error?', 'answer': '`relativeSD`', 'why': 'The maximum relative standard deviation; smaller means more accurate.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Which algorithm does Databricks SQL’s `approx_count_distinct` use?', 'answer': 'HyperLogLog++ (HLL++)', 'why': 'The dense version of HLL++ estimates distinct values without remembering each one.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'In Databricks SQL, a dashboard shows distinct visitors per day over billions of events. An error of a few percent is fine, but the query must be fast.\n\nWhich expression fits?', 'pick': 1,
       'correct': [opt(AC['approx'], 'Estimates distinct values within about 5% by default, built for speed at scale.')],
       'distractors': [opt(AC['exact'], 'Exact, which the dashboard doesn’t need.'),
                       opt(AC['sumd'], 'Adds up the distinct ID values; it doesn’t count them.'),
                       opt(AC['loose'], 'Loosens the error to 10%, more than a few percent.'),
                       opt(AC['tight'], 'Tightens the error to 1%, which the dashboard doesn’t need.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'In Databricks SQL, a finance reconciliation needs the exact number of distinct invoice IDs per month. It runs overnight, so speed isn’t a concern.\n\nWhich expression fits?', 'pick': 1,
       'correct': [opt(AC['exact'], 'Counts every distinct value exactly.')],
       'distractors': [opt(AC['approx'], 'An estimate within about 5%, not exact.'),
                       opt(AC['tight'], 'Closer, but still an estimate.'),
                       opt(AC['loose'], 'An estimate within about 10%.'),
                       opt(AC['sumd'], 'Adds up the distinct invoice IDs; it doesn’t count them.')]},
      {'id': 's3', 'stem': 'In Databricks SQL, a team uses `approx_count_distinct(id)` and wants to keep it, but tighten its error from the default to about 1%.\n\nWhich expression fits?', 'pick': 1,
       'correct': [opt(AC['tight'], 'Sets `relativeSD` to 0.01, a tighter error than the 5% default.')],
       'distractors': [opt(AC['approx'], 'Keeps the default error of about 5%.'),
                       opt(AC['loose'], 'Loosens the error to 10%.'),
                       opt(AC['exact'], 'Exact, but they want to keep the approximate function.'),
                       opt(AC['sumd'], 'Adds up the distinct IDs; it doesn’t count them.')]},
    ], setting=['SQL'], rev=1))
  EVIDENCE['dea-3-4-approx-distinct'] = [(0, r'Returns the estimated number of distinct values'), (0, r'dense version of the HyperLogLog\+\+'),
    (0, r'accurate within a default value of 5%'), (0, r'`relativeSD`: Defines the maximum relative standard deviation allowed')]
  return C

def chunk4(concept, opt):
  C = []
  L = D + '/sql/language-manual'
  G = D + '/data-governance/unity-catalog'
  # ---------- 3.5 adaptive query execution ----------
  JS = {'bhj': 'A broadcast hash join, switched by AQE', 'smj': 'The planned sort merge join', 'cross': 'A cross join of the two tables',
        'fact': 'A broadcast of the large fact table', 'skew': 'Skew splitting of every join task'}
  C.append(concept('dea-3-5-aqe', '3', '3.5', 41, 'Adaptive query execution and shuffle tuning',
    [{'title': 'Adaptive query execution', 'url': D + '/optimizations/aqe'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'Is Spark adaptive query execution (AQE) on by default in Databricks?', 'answer': 'Yes', 'why': 'Check whether it changed a plan when troubleshooting; tune its settings only when the defaults don’t fit.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'Which three things can Spark adaptive query execution change at runtime?', 'answer': 'Join strategy, post-shuffle partition count, and skewed join tasks', 'why': 'Using runtime statistics, it switches sort merge joins to broadcast, coalesces small partitions and splits skewed tasks.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'Below what size does Spark adaptive query execution switch a sort merge join to a broadcast hash join at runtime?', 'answer': '30 MB, by default', 'why': 'Set by `spark.databricks.adaptive.autoBroadcastJoinThreshold`.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'What is the default of `spark.sql.shuffle.partitions` in Spark, and what does `auto` do?', 'answer': '200; `auto` sizes it from the query plan and input', 'why': '`auto` turns on auto-optimized shuffle instead of a fixed count.'},
      {'id': 'r5', 'type': 'symptom', 'prompt': 'A Spark query plan shows a `CustomShuffleReader` node marked `Coalesced`. What did adaptive query execution do?', 'answer': 'Combined small post-shuffle partitions', 'why': 'Tiny tasks waste time on scheduling, so AQE merges them into reasonably sized ones.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A Spark job joins a large fact table to a dimension that is 15 MB after filtering. Stale statistics make the plan pick a sort merge join. Adaptive query execution is on with default settings.\n\nWhich join runs?', 'pick': 1,
       'correct': [opt(JS['bhj'], 'At runtime the dimension is under the 30 MB threshold, so AQE broadcasts it.')],
       'distractors': [opt(JS['smj'], 'AQE corrects the plan once the real size is known.'),
                       opt(JS['cross'], 'The join has a condition, so it isn’t a cross join.'),
                       opt(JS['fact'], 'AQE broadcasts the small side, not the fact table.'),
                       opt(JS['skew'], 'Skew handling splits only oversized tasks, and nothing here is skewed.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A Spark job joins a large fact table to a dimension that is 300 MB after filtering. The plan picks a sort merge join. Adaptive query execution is on with default settings, and there are no hints.\n\nWhich join runs?', 'pick': 1,
       'correct': [opt(JS['smj'], '300 MB is over the 30 MB runtime threshold, so the plan stands.')],
       'distractors': [opt(JS['bhj'], 'AQE switches only below its 30 MB threshold.'),
                       opt(JS['cross'], 'The join has a condition, so it isn’t a cross join.'),
                       opt(JS['fact'], 'Nothing broadcasts the large fact table.'),
                       opt(JS['skew'], 'Skew handling splits only oversized tasks, and nothing here is skewed.')]},
      {'id': 's3', 'stem': 'A Spark job filters out most rows, then shuffles into thousands of tiny partitions that each finish in milliseconds. The team wants fewer, reasonably sized tasks without hand-tuning.\n\nWhich feature handles this?', 'pick': 1,
       'correct': [opt('Adaptive partition coalescing, on by default', 'AQE merges small post-shuffle partitions into reasonably sized ones.')],
       'distractors': [opt('A `BROADCAST` hint on the source table', 'Changes the join strategy, not the partition count.'),
                       opt('Salting the grouping key in two passes', 'Spreads a hot key; the problem is too many tiny partitions.'),
                       opt('Liquid clustering on the source table', 'Changes file layout on disk, not shuffle partitions.'),
                       opt('More executors of the same size', 'More slots for the same tiny tasks.')]},
    ], setting=['Spark', 'adaptive query execution'], rev=1))
  EVIDENCE['dea-3-5-aqe'] = [(0, r'AQE is enabled by default'), (0, r'Dynamically changes sort merge join into broadcast hash join'),
    (0, r'Dynamically coalesces partitions'), (0, r'Dynamically handles skew in sort merge join and shuffle hash join'),
    (0, r'`spark\.databricks\.adaptive\.autoBroadcastJoinThreshold` \| `Byte String` \| `30MB`'),
    (0, r'`spark\.sql\.shuffle\.partitions` \| `Integer` \| `200`'), (0, r'Set it to `auto` to enable auto-optimized shuffle'),
    (0, r'`CustomShuffleReader` node with the `Coalesced` property')]

  # ---------- 3.2 joins and the broadcast hint ----------
  JN = {'left': 'A `LEFT JOIN` to the stores table', 'inner': 'An inner `JOIN` to the stores table', 'anti': 'A `LEFT ANTI JOIN` to the stores table',
        'semi': 'A `LEFT SEMI JOIN` to the stores table', 'cross': 'A `CROSS JOIN` with the stores table'}
  C.append(concept('dea-3-2-joins', '3', '3.2', 42, 'Join types and the broadcast hint',
    [{'title': 'JOIN', 'url': L + '/sql-ref-syntax-qry-select-join'}, {'title': 'Hints', 'url': L + '/sql-ref-syntax-qry-select-hints'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In Databricks SQL, what does a `LEFT JOIN` return for a left row with no match?', 'answer': 'The left row, with NULLs for the right columns', 'why': 'Every left row is kept; an inner join would drop it.'},
      {'id': 'r2', 'type': 'code', 'prompt': 'In Databricks SQL, list customers who have never placed an order.', 'lang': 'sql', 'code': 'SELECT c.customer_id\nFROM crm.silver.customers c\nLEFT {{gap}} JOIN shop.silver.orders o\n  ON c.customer_id = o.customer_id;', 'answer': 'ANTI', 'why': 'A left anti join returns left rows with no match on the right.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In Databricks SQL, what does a join with no join condition become?', 'answer': 'A cross join: the Cartesian product', 'why': 'Omitting the criteria gives any join type the semantics of `CROSS JOIN`.'},
      {'id': 'r4', 'type': 'code', 'prompt': 'In Databricks SQL, make the small `stores` table broadcast to every executor.', 'lang': 'sql', 'code': 'SELECT /*+ {{gap}}(s) */ o.*, s.region\nFROM sales.silver.orders o\nJOIN ref.core.stores s\n  ON o.store_id = s.store_id;', 'answer': 'BROADCAST', 'why': 'The hinted side is broadcast regardless of the threshold; `BROADCASTJOIN` and `MAPJOIN` are aliases.', 'src': 1},
      {'id': 'r5', 'type': 'basic', 'prompt': 'In Databricks SQL, which join returns left rows that have a match, without adding right-side columns?', 'answer': 'A left semi join', 'why': 'It filters the left side by existence of a match; a left anti join keeps the non-matches.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'In Databricks SQL, a silver step must keep every order and add the store’s region where a matching store record exists.\n\nWhich join fits?', 'pick': 1,
       'correct': [opt(JN['left'], 'Keeps every order, with NULL regions where no store matches.')],
       'distractors': [opt(JN['inner'], 'Drops orders whose store has no record.'),
                       opt(JN['anti'], 'Keeps only orders with no store match, and no region.'),
                       opt(JN['semi'], 'Keeps matching orders but adds no store columns.'),
                       opt(JN['cross'], 'Pairs every order with every store.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'In Databricks SQL, a silver step must keep only orders whose store exists in the stores table, with the store’s region added.\n\nWhich join fits?', 'pick': 1,
       'correct': [opt(JN['inner'], 'Returns only matching orders, with the store’s columns available.')],
       'distractors': [opt(JN['left'], 'Also keeps orders with no store, as NULLs.'),
                       opt(JN['anti'], 'Keeps the orders that don’t match.'),
                       opt(JN['semi'], 'Keeps matching orders but can’t add the region.'),
                       opt(JN['cross'], 'Pairs every order with every store.')]},
      {'id': 's3', 'stem': 'In Databricks SQL, a data quality check must list orders whose `store_id` has no match in the stores table, to find broken references.\n\nWhich join fits?', 'pick': 1,
       'correct': [opt(JN['anti'], 'Returns exactly the left rows with no match on the right.')],
       'distractors': [opt(JN['left'], 'Returns every order; the broken ones still need a filter.'),
                       opt(JN['inner'], 'Returns only the orders that do match.'),
                       opt(JN['semi'], 'Returns only the orders that do match.'),
                       opt(JN['cross'], 'Pairs every order with every store.')]},
    ], setting=['SQL'], rev=1))
  EVIDENCE['dea-3-2-joins'] = [(0, r'Returns all values from the left table reference and the matched values from the right table reference, or appends `NULL`'),
    (0, r'Returns the values from the left table reference that have no match with the right table reference'),
    (0, r'Returns values from the left side of the table reference that has a match with the right'),
    (0, r'If you omit the `join_criteria` the semantic of any `join_type` becomes that of a `CROSS JOIN`'),
    (0, r'Returns the Cartesian product of two relations'),
    (1, r'The join side with the hint is broadcast regardless of `autoBroadcastJoinThreshold`'), (1, r'`BROADCASTJOIN` and `MAPJOIN` are supported as aliases')]

  # ---------- 3.6 materialized view refresh ----------
  MR = {'trig': 'Create it with `TRIGGER ON UPDATE`', 'cron': 'Create it with a nightly `SCHEDULE CRON`', 'manual': 'Run `REFRESH MATERIALIZED VIEW` once',
        'std': 'Replace it with a standard view', 'every': 'Create it with `SCHEDULE EVERY 1 HOUR`'}
  C.append(concept('dea-3-6-mv-refresh', '3', '3.6', 43, 'Refreshing materialized views',
    [{'title': 'Use standalone materialized views', 'url': D + '/sql/mv-st/materialized'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In Databricks SQL, refresh a materialized view automatically whenever its source table changes.', 'lang': 'sql', 'code': 'CREATE OR REPLACE MATERIALIZED VIEW\n  sales.gold.daily_rev\n{{gap}} ON UPDATE\nAS SELECT order_date,\n  sum(amount) AS revenue\nFROM sales.silver.orders\nGROUP BY order_date;', 'answer': 'TRIGGER', 'why': 'Suited to production when upstream loads don’t run on a predictable schedule.'},
      {'id': 'r2', 'type': 'comparison', 'prompt': 'In Databricks SQL, standard view or materialized view: which computes its results on demand at query time?', 'answer': 'The standard view', 'why': 'A materialized view stores the results and updates them as the sources change.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'What does Databricks create to process a materialized view’s refreshes when the view is defined in a SQL warehouse?', 'answer': 'A serverless pipeline', 'why': 'Refresh status shows in Catalog Explorer.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'How do you refresh a standalone materialized view by hand in Databricks SQL?', 'answer': '`REFRESH MATERIALIZED VIEW <name>`', 'why': 'It refreshes without recreating the view or changing its schedule.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'Who owns a standalone materialized view in Databricks SQL?', 'answer': 'The user who created it', 'why': 'The creator becomes the materialized view’s owner.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A gold materialized view in Databricks SQL feeds a dashboard. Another team loads its source table at unpredictable times, and the view should be current soon after each load.\n\nHow should it refresh?', 'pick': 1,
       'correct': [opt(MR['trig'], 'Refreshes whenever the source changes, which suits unpredictable loads.')],
       'distractors': [opt(MR['cron'], 'Runs at a fixed time, so it lags loads that land at other times.'),
                       opt(MR['manual'], 'Refreshes once, then relies on someone remembering.'),
                       opt(MR['std'], 'Recomputes on every dashboard query instead of storing results.'),
                       opt(MR['every'], 'Polls hourly, refreshing when nothing changed and lagging when it did.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A gold materialized view in Databricks SQL feeds a finance report. The source is updated hourly, but finance wants the figures to change only once a day, at 03:30 UTC.\n\nHow should it refresh?', 'pick': 1,
       'correct': [opt(MR['cron'], 'A daily CRON schedule at 03:30 UTC refreshes once a day, at that time.')],
       'distractors': [opt(MR['trig'], 'Would refresh after every hourly update.'),
                       opt(MR['manual'], 'Depends on someone running it each night.'),
                       opt(MR['std'], 'Would always show the latest hourly data.'),
                       opt(MR['every'], 'Refreshes every hour, not once a day.')]},
      {'id': 's3', 'stem': 'A scheduled materialized view in Databricks SQL must reflect a backfill that just finished. Its nightly schedule must stay as it is.\n\nWhat should the engineer do?', 'pick': 1,
       'correct': [opt(MR['manual'], 'Refreshes it now without changing its schedule.')],
       'distractors': [opt(MR['trig'], 'Changes how it refreshes from now on.'),
                       opt(MR['cron'], 'Recreates it with a schedule instead of refreshing now.'),
                       opt(MR['std'], 'Throws away the stored results and the schedule.'),
                       opt(MR['every'], 'Replaces the nightly schedule with an hourly one.')]},
    ], setting=['materialized view'], rev=1))
  EVIDENCE['dea-3-6-mv-refresh'] = [(0, r'Unlike standard views, which compute results on demand, materialized views cache the results'),
    (0, r'automatically refreshes whenever the upstream source data changes using `TRIGGER ON UPDATE`'),
    (0, r'especially when upstream dependencies don\'t run on predictable schedules'), (0, r'MATERIALIZED VIEW mv_trigger\s*\nTRIGGER ON UPDATE'),
    (0, r'SCHEDULE CRON \'0 30 3 \* \* \?\' AT TIME ZONE \'UTC\''), (0, r'`SCHEDULE EVERY` syntax'), (0, r'REFRESH MATERIALIZED VIEW mv1;'),
    (0, r'a \[serverless pipeline\]\(/aws/en/ldp/serverless\) is created to process the create and refreshes'),
    (0, r'The user who creates a materialized view is the materialized view owner')]

  # ---------- 3.7 Python expectations ----------
  C.append(concept('dea-3-7-python-expectations', '3', '3.7', 44, 'Expectations in Python pipelines',
    [{'title': 'Manage data quality with pipeline expectations', 'url': D + '/ldp/expectations'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In a Lakeflow Declarative Pipeline in Python, drop rows with a negative price and keep the update running.', 'lang': 'python', 'code': '@dp.table\n@dp.{{gap}}("valid_price",\n  "price >= 0")\ndef silver_items():\n  return spark.readStream.table(\n    "bronze_items")', 'answer': 'expect_or_drop', 'why': 'Invalid rows are dropped before the write, and the drop count is logged.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'In a Lakeflow Declarative Pipeline in Python, which decorator applies a dictionary of expectations and fails the update on any violation?', 'answer': '`@dp.expect_all_or_fail`', 'why': 'The `expect_all` family takes a dict of name to constraint, with warn, drop and fail versions.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In a Lakeflow Declarative Pipeline in Python, which expectation decorator keeps invalid rows and only records them?', 'answer': '`@dp.expect`', 'why': 'Warn is the default action, like SQL `EXPECT` with no `ON VIOLATION`.'},
      {'id': 'r4', 'type': 'comparison', 'prompt': 'A Lakeflow Declarative Pipeline expectation uses SQL `ON VIOLATION FAIL UPDATE`. Which Python decorator does the same?', 'answer': '`@dp.expect_or_fail`', 'why': 'Invalid records stop the update, and someone must intervene before it reruns.'},
    ], setting=['Lakeflow Declarative Pipeline'], rev=1))
  EVIDENCE['dea-3-7-python-expectations'] = [(0, r'\| `EXPECT \.\.\. ON VIOLATION DROP ROW` \| `dp\.expect_or_drop` \|'),
    (0, r'\| `EXPECT \.\.\. ON VIOLATION FAIL UPDATE` \| `dp\.expect_or_fail` \|'), (0, r'\(default\) \| `EXPECT` \| `dp\.expect` \|'),
    (0, r'`expect_all`, `expect_all_or_drop`, and `expect_all_or_fail`'), (0, r'accept a Python dictionary as an argument'),
    (0, r'@dp\.table'), (0, r'The count of dropped records is logged')]

  # ---------- 3.6 AUTO CDC ----------
  AU = {'s1': '`AUTO CDC`, stored as SCD type 1', 's2': '`AUTO CDC`, stored as SCD type 2', 'snap': '`AUTO CDC FROM SNAPSHOT`, SCD type 1',
        'append': 'A streaming table appending each event', 'mv': 'A materialized view of the latest rows'}
  C.append(concept('dea-3-6-auto-cdc', '3', '3.6', 45, 'Applying change feeds with AUTO CDC',
    [{'title': 'The AUTO CDC APIs: Simplify change data capture with pipelines', 'url': D + '/ldp/cdc'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In a Lakeflow Declarative Pipeline, which API replaces `APPLY CHANGES` for change data capture?', 'answer': '`AUTO CDC`, with the same syntax', 'why': '`APPLY CHANGES` still works, but Databricks recommends `AUTO CDC`.'},
      {'id': 'r2', 'type': 'code', 'prompt': 'In a Lakeflow Declarative Pipeline, order change events by `change_ts` so late arrivals apply correctly.', 'lang': 'sql', 'code': "CREATE FLOW customers_cdc AS\nAUTO CDC INTO silver_customers\nFROM stream(bronze_customer_cdc)\nKEYS (customer_id)\nAPPLY AS DELETE WHEN op = 'DELETE'\n{{gap}} change_ts\nSTORED AS SCD TYPE 2;", 'answer': 'SEQUENCE BY', 'why': 'Sequencing decides which change is newest, whatever order events arrive in.'},
      {'id': 'r3', 'type': 'decision', 'prompt': 'In a Lakeflow Declarative Pipeline, the source can’t produce a change feed, only periodic full snapshots. Which API applies the changes?', 'answer': '`AUTO CDC FROM SNAPSHOT`', 'why': 'It compares snapshots to work out the changes, then applies them.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'In a Lakeflow Declarative Pipeline, what must exist before an `AUTO CDC ... INTO` flow can write?', 'answer': 'A streaming table as its target', 'why': 'Create the streaming table first, then define the flow into it.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'In a Lakeflow Declarative Pipeline `AUTO CDC` flow, how do you sequence by a timestamp and break ties with an ID?', 'answer': '`SEQUENCE BY STRUCT(ts, id)`', 'why': 'It orders by the first field, then the next field on a tie.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'A Lakeflow Declarative Pipeline receives a change feed of customer inserts, updates and deletes, sometimes out of order. The silver table must hold only each customer’s latest state.\n\nWhich setup fits?', 'pick': 1,
       'correct': [opt(AU['s1'], 'Applies changes in sequence order and keeps only the latest version of each key.')],
       'distractors': [opt(AU['s2'], 'Keeps every past version, which isn’t wanted here.'),
                       opt(AU['snap'], 'For sources with only snapshots; this one has a change feed.'),
                       opt(AU['append'], 'Keeps every event as a row and never applies updates or deletes.'),
                       opt(AU['mv'], 'Recomputes from all events and leaves out-of-order and delete handling to you.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'A Lakeflow Declarative Pipeline receives a change feed of customer inserts, updates and deletes, sometimes out of order. The silver table must keep every past version of each customer.\n\nWhich setup fits?', 'pick': 1,
       'correct': [opt(AU['s2'], 'Retains a history row per change, ordered by the sequence column.')],
       'distractors': [opt(AU['s1'], 'Overwrites each customer with the latest version.'),
                       opt(AU['snap'], 'For sources with only snapshots; this one has a change feed.'),
                       opt(AU['append'], 'Keeps raw events, not versioned customer records.'),
                       opt(AU['mv'], 'Shows current rows, not a version history.')]},
      {'id': 's3', 'stem': 'A Lakeflow Declarative Pipeline ingests a nightly full export of a vendor table. The vendor offers no change feed, and silver must reflect inserts, updates and deletes, keeping only current rows.\n\nWhich setup fits?', 'pick': 1,
       'correct': [opt(AU['snap'], 'Compares each snapshot with the last to find the changes.')],
       'distractors': [opt(AU['s1'], 'Needs a change feed, which the vendor doesn’t offer.'),
                       opt(AU['s2'], 'Needs a change feed, and keeps history that isn’t wanted.'),
                       opt(AU['append'], 'Appends each full export, duplicating rows nightly.'),
                       opt(AU['mv'], 'Can’t tell deleted rows from the latest export alone.')]},
    ], setting=['Lakeflow Declarative Pipeline'], rev=1))
  EVIDENCE['dea-3-6-auto-cdc'] = [(0, r'The `AUTO CDC` APIs replace the `APPLY CHANGES` APIs and have the same syntax'),
    (0, r'Use this when CDC is not enabled on the source database and only snapshots are available'),
    (0, r'create a streaming table and then use the `AUTO CDC \.\.\. INTO` statement'), (0, r'SEQUENCE BY STRUCT\(timestamp_col, id_col\)'),
    (0, r'Use SCD Type 1 to update records directly\. History is not retained'), (0, r'Use SCD Type 2 to retain a history of records'),
    (0, r'CREATE FLOW apply_cdc AS AUTO CDC INTO'), (0, r'APPLY AS DELETE WHEN'), (0, r'This batch of updates arrived out of order')]

  # ---------- 7.1 managed and external tables ----------
  MX = {'mgd': 'A Unity Catalog managed table', 'ext': 'An external table on an external location', 'fed': 'A foreign table through Lakehouse Federation',
        'mv': 'A materialized view over the raw files', 'vol': 'Files in a volume with no table'}
  C.append(concept('dea-7-1-managed-external', '7', '7.1', 46, 'Managed and external tables',
    [{'title': 'Unity Catalog managed tables for Delta Lake and Apache Iceberg', 'url': D + '/tables/managed'}, {'title': 'Work with external tables', 'url': D + '/tables/external'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In Unity Catalog, you `DROP` a managed table. What happens to its data files?', 'answer': 'They’re deleted after the recovery period, 7 days by default', 'why': '`UNDROP TABLE` can recover it within that period.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'In Unity Catalog, you `DROP` an external table. What happens to its data files?', 'answer': 'Nothing: only the metadata is removed', 'why': 'You must delete the files from storage yourself.', 'src': 1},
      {'id': 'r3', 'type': 'basic', 'prompt': 'Which Unity Catalog command recovers a managed table dropped by mistake?', 'answer': '`UNDROP TABLE`', 'why': 'By default within 7 days; the period can be set to 0, or 7 to 30 days.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'What must a Unity Catalog external table specify that a managed table doesn’t?', 'answer': 'A `LOCATION` inside a registered external location', 'why': 'Creating it also needs `CREATE EXTERNAL TABLE` on that external location.', 'src': 1},
      {'id': 'r5', 'type': 'basic', 'prompt': 'Which table type does Databricks recommend by default in Unity Catalog?', 'answer': 'Managed tables', 'why': 'Unity Catalog handles storage and optimization, with predictive optimization and faster queries.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'In Unity Catalog, a silver table is read and written only from Databricks. The team wants automatic optimization, and dropped data cleaned up without manual file deletion.\n\nWhich table type fits?', 'pick': 1,
       'correct': [opt(MX['mgd'], 'Unity Catalog manages storage and optimization, and deletes files after a drop.')],
       'distractors': [opt(MX['ext'], 'Unity Catalog doesn’t manage its files, so a drop leaves them behind.'),
                       opt(MX['fed'], 'Read-only access to another system, not a silver table you write.'),
                       opt(MX['mv'], 'Stores a query result, not a table you write to.'),
                       opt(MX['vol'], 'Volumes hold files, not governed tables.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'In Unity Catalog, a silver table must also be read straight from storage by a non-Databricks engine that supports no other external access pattern.\n\nWhich table type fits?', 'pick': 1,
       'correct': [opt(MX['ext'], 'Databricks recommends external tables when non-Databricks clients need direct file access.')],
       'distractors': [opt(MX['mgd'], 'Recommended by default, but this engine needs direct access to the files.'),
                       opt(MX['fed'], 'Reads another system’s data; it doesn’t expose this table’s files.'),
                       opt(MX['mv'], 'A stored query result, not a table for external engines.'),
                       opt(MX['vol'], 'Files with no table, so Databricks users lose the table.')]},
      {'id': 's3', 'stem': 'In Unity Catalog, an engineer drops the external table `ext_sales` and the managed table `mgd_sales` by mistake, with default settings.\n\nWhich two statements are true?', 'pick': 2,
       'correct': [opt('The `mgd_sales` files go after 7 days unless undropped', 'Managed table files are purged when the recovery period ends.'),
                   opt('The `ext_sales` files stay in cloud storage', 'Dropping an external table removes only its metadata.')],
       'distractors': [opt('The `ext_sales` files go after 7 days', 'Unity Catalog never deletes an external table’s files.'),
                       opt('The `mgd_sales` files are deleted at once', 'They’re kept for the 7-day recovery period.'),
                       opt('Both tables’ files stay in storage for good', 'The managed table’s files are purged after 7 days.'),
                       opt('The `mgd_sales` table can’t be recovered', '`UNDROP TABLE` recovers it within 7 days.')]},
    ], setting=['Unity Catalog'], rev=1))
  EVIDENCE['dea-7-1-managed-external'] = [(0, r'Unity Catalog managed tables are the default and recommended table type'),
    (0, r'deletes the data files in cloud storage after the recovery period expires \(default 7 days\)'),
    (0, r'Unity Catalog supports the \[UNDROP TABLE\]'), (0, r'The recovery period can be 0 hours, which disables recovery, or 7 to 30 days'),
    (1, r'When you drop an external table, Unity Catalog removes the table metadata but does not delete the underlying data files'),
    (1, r'you must specify a storage location\. This location is an \[external location\]'), (1, r'The `CREATE EXTERNAL TABLE` privilege on an external location'),
    (1, r'direct access to the data from non-Databricks clients that don\'t support other external access patterns')]

  # ---------- 7.1 converting to managed ----------
  C.append(concept('dea-7-1-set-managed', '7', '7.1', 47, 'Converting external tables to managed',
    [{'title': 'Convert external or foreign Delta Lake tables to Unity Catalog managed tables', 'url': D + '/tables/convert-to-managed'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In Unity Catalog, convert an external Delta table to a managed table in place.', 'lang': 'sql', 'code': 'ALTER TABLE sales.bronze.orders_ext\n  SET {{gap}};', 'answer': 'MANAGED', 'why': 'For an external table, `SET MANAGED` takes no `MOVE` or `COPY` option.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'Why does Databricks recommend `SET MANAGED` over CTAS to convert a Unity Catalog external table?', 'answer': 'It keeps the table and minimizes reader and writer downtime', 'why': 'CTAS creates a new table; `SET MANAGED` converts the existing one in place.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'After converting a Unity Catalog external table with `SET MANAGED`, how long can you roll back, and with what?', 'answer': '14 days, with `UNSET MANAGED`', 'why': 'It points the table back at its original external location.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Converting a Unity Catalog external table, what happens if you add `MOVE` or `COPY` to `SET MANAGED`?', 'answer': 'It fails: those options are for foreign tables', 'why': 'External tables use plain `SET MANAGED`; foreign tables must choose `MOVE` or `COPY`.'},
      {'id': 'r5', 'type': 'basic', 'prompt': 'Which compute can run Unity Catalog `SET MANAGED`?', 'answer': 'Databricks Runtime 17.3 LTS or above, or serverless', 'why': 'The same applies to `UNSET MANAGED`.'},
    ], setting=['Unity Catalog'], rev=1))
  EVIDENCE['dea-7-1-set-managed'] = [(0, r'use the \[`ALTER TABLE \.\.\. SET MANAGED`\]'), (0, r'Minimizes reader and writer downtime'),
    (0, r'Databricks recommends `SET MANAGED` for the preceding benefits'), (0, r'roll back within 14 days by using the `UNSET MANAGED` command'),
    (0, r'DELTA_ALTER_TABLE_SET_MANAGED_UNSUPPORTED_COPY_MOVE_SYNTAX'), (0, r'You must specify either `MOVE` or `COPY`'),
    (0, r'Databricks Runtime 17\.3 LTS or above or Serverless compute to use `SET MANAGED`, `UNSET MANAGED`')]

  # ---------- 7.4 ABAC policies ----------
  C.append(concept('dea-7-4-abac-policies', '7', '7.4', 48, 'ABAC row filter and column mask policies',
    [{'title': 'CREATE POLICY', 'url': L + '/sql-ref-syntax-ddl-create-policy'}, {'title': 'Create and manage row filter and column mask policies', 'url': G + '/abac/policies'},
     {'title': 'Attribute-based access control in Unity Catalog', 'url': G + '/abac/'}, {'title': 'When to use ABAC vs table-level row filters and column masks', 'url': G + '/abac/abac-vs-rls-cm'}],
    [
      {'id': 'r1', 'type': 'code', 'prompt': 'In Unity Catalog ABAC, mask every column tagged `pii` in the schema, except for `hr_admins`.', 'lang': 'sql', 'code': "CREATE POLICY mask_pii\nON SCHEMA hr.core\nCOLUMN MASK hr.sec.redact\nTO `account users`\nEXCEPT `hr_admins`\nFOR TABLES\n{{gap}} has_tag('pii') AS c\nON COLUMN c;", 'answer': 'MATCH COLUMNS', 'why': 'It picks columns by their governed tags; `ON COLUMN` passes the match to the mask.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'In Unity Catalog ABAC, where can a row filter or column mask policy be attached?', 'answer': 'A catalog, schema or table (metastore in Beta)', 'why': 'It covers every table in that scope, evaluated dynamically.', 'src': 2},
      {'id': 'r3', 'type': 'basic', 'prompt': 'What do Unity Catalog ABAC policies use to match tables and columns?', 'answer': 'Governed tags', 'why': 'Through `has_tag()` and `has_tag_value()` in the policy’s conditions.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'Which privileges do you need to create a Unity Catalog ABAC policy?', 'answer': '`MANAGE` on (or ownership of) the scope, plus `EXECUTE` on the UDF', 'why': 'The UDF holds the filtering or masking logic.', 'src': 1},
      {'id': 'r5', 'type': 'basic', 'prompt': 'In a Unity Catalog ABAC policy, which clause exempts principals so they see unfiltered, unmasked data?', 'answer': '`EXCEPT`', 'why': '`TO` lists who the policy applies to; `EXCEPT` lists who is exempt.'},
    ],
    [
      {'id': 's1', 'stem': 'In Unity Catalog, an ABAC row filter policy on the `sales` catalog limits rows by region. The compliance auditors group must see every row; nothing else should change.\n\nWhat should the policy owner do?', 'pick': 1,
       'correct': [opt('Add the auditors to the policy’s `EXCEPT` list', 'Exempt principals see full, unfiltered data.')],
       'distractors': [opt('Grant the auditors `MANAGE` on the catalog', 'Lets them manage grants and policies, not bypass the filter.'),
                       opt('Remove the governed tag from the tables', 'Stops the filter for everyone, not just the auditors.'),
                       opt('Grant the auditors `SELECT` on every table', 'They still read through the row filter.'),
                       opt('Add a table-level filter for the auditors', 'Evaluated alongside the policy; it can’t lift it.')]},
      {'id': 's2', 'stem': 'In Unity Catalog, an engineer with `MANAGE` on the `crm` catalog wants to create an ABAC column mask policy there, on serverless compute.\n\nWhich two must also be in place?', 'pick': 2,
       'correct': [opt('`EXECUTE` on the masking UDF', 'The UDF holds the masking logic, so the creator needs `EXECUTE` on it.'),
                   opt('Governed tags on the target columns', 'The policy finds the columns to mask by their tags.')],
       'distractors': [opt('Ownership of every table in scope', '`MANAGE` on the catalog is enough.'),
                       opt('A column mask on each table first', 'The policy replaces per-table masks.'),
                       opt('Metastore admin rights', 'Needed only for metastore-level policies.'),
                       opt('A dedicated classic cluster', 'Serverless compute meets the requirement.')]},
      {'id': 's3', 'stem': 'In Unity Catalog, a column mask policy on the `crm.core` schema matches columns with `has_tag(\'pii\')`. A new table is created there with a column tagged `pii`.\n\nWhat happens to that column?', 'pick': 1,
       'correct': [opt('It’s masked by the policy automatically', 'New tagged tables in scope are covered with no extra step.')],
       'distractors': [opt('It stays unmasked until the policy is recreated', 'Policies match dynamically; nothing needs recreating.'),
                       opt('It’s masked only after an `ALTER TABLE`', 'That sets a table-level mask, which isn’t needed here.'),
                       opt('It stays unmasked until its owner opts in', 'Table owners can’t opt out of, or into, a schema policy.'),
                       opt('It’s hidden from every user entirely', 'A mask changes values; it doesn’t hide the column.')]},
    ], setting=['Unity Catalog'], rev=1))
  EVIDENCE['dea-7-4-abac-policies'] = [(0, r'CREATE \[ OR REPLACE \] POLICY policy_name'), (0, r'ON \{ METASTORE \| CATALOG catalog_name \| SCHEMA schema_name \| TABLE table_name'),
    (0, r'MATCH COLUMNS condition'), (0, r'ON COLUMN alias'), (0, r'Principals listed after `EXCEPT` are excluded from the policy'), (0, r'has_tag\(\'pii\'\)'),
    (1, r'you must have `MANAGE` on the securable object where the policy is attached \(catalog, schema, or table\) or own the securable object, and `EXECUTE` on the UDF'),
    (1, r'Governed tags applied to target objects'), (1, r'Databricks Runtime 16\.4 or above, or serverless compute'),
    (1, r'Exempt principals are not subject to filtering or masking and see the full, unmodified data'),
    (2, r'such as a metastore \(Beta\), catalog, schema, or table, and are evaluated dynamically'),
    (3, r'New tagged tables are covered automatically'), (3, r'table owners cannot override, modify, or remove them'),
    (3, r'the policies are evaluated independently')]

  # ---------- 7.4 ABAC or table-level filters and masks ----------
  AV = {'abac': 'An ABAC policy on the catalog', 'tbl': 'A table-level mask set with `ALTER TABLE`', 'grant': 'An ABAC GRANT policy on the catalog',
        'view': 'A dynamic view in front of each table', 'filter': 'A row filter on each table'}
  C.append(concept('dea-7-4-abac-vs-table', '7', '7.4', 49, 'ABAC policies or table-level filters and masks',
    [{'title': 'When to use ABAC vs table-level row filters and column masks', 'url': G + '/abac/abac-vs-rls-cm'}],
    [
      {'id': 'r1', 'type': 'comparison', 'prompt': 'In Unity Catalog, an ABAC policy set on the catalog or a table-level column mask: which can a table owner remove from their own table?', 'answer': 'The table-level column mask', 'why': 'Once a policy is set at a higher level, table owners can’t override, modify or remove it.'},
      {'id': 'r2', 'type': 'comparison', 'prompt': 'In Unity Catalog, ABAC policies or table-level row filters: which cover newly tagged tables automatically?', 'answer': 'ABAC policies', 'why': 'Table-level filters and masks must be set on each table individually.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In Unity Catalog, which command shows the ABAC policies that apply to a given table and user?', 'answer': '`SHOW EFFECTIVE POLICIES`', 'why': 'Table-level filters and masks show directly on the table definition instead.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'In Unity Catalog, which SQL sets a table-level row filter, as opposed to an ABAC policy?', 'answer': '`ALTER TABLE ... SET ROW FILTER`', 'why': 'ABAC uses `CREATE POLICY ... ON CATALOG/SCHEMA/TABLE`.'},
    ],
    [
      {'id': 's1', 'flip': 's2', 'stem': 'In Unity Catalog, a governance team must mask every column tagged `pii` across 400 tables in the `crm` catalog, including tables created later. Table owners must not be able to remove the masking.\n\nWhich approach fits?', 'pick': 1,
       'correct': [opt(AV['abac'], 'Covers every tagged column in scope, new tables included, and owners can’t remove it.')],
       'distractors': [opt(AV['tbl'], 'Must be set on all 400 tables, and owners can remove it.'),
                       opt(AV['grant'], 'Grants privileges dynamically; it doesn’t mask values.'),
                       opt(AV['view'], 'One view per table to build and keep in sync, and the tables stay exposed.'),
                       opt(AV['filter'], 'Hides rows rather than masking columns, table by table.')]},
      {'id': 's2', 'flip': 's1', 'stem': 'In Unity Catalog, one table, `hr.core.salaries`, needs a column mask with logic that fits no other table. Its owner wants to manage the mask directly, and there’s no governed tag system.\n\nWhich approach fits?', 'pick': 1,
       'correct': [opt(AV['tbl'], 'Specific logic on one table, managed by its owner, with no tags needed.')],
       'distractors': [opt(AV['abac'], 'Needs governed tags and is managed above the table, not by its owner.'),
                       opt(AV['grant'], 'Grants privileges; it doesn’t mask values.'),
                       opt(AV['view'], 'Leaves the base table unmasked for anyone who can read it.'),
                       opt(AV['filter'], 'Hides rows, but the need is to mask a column.')]},
      {'id': 's3', 'stem': 'In Unity Catalog, policy authors define the access rules while data stewards classify data with tags. New tables arrive every week across several schemas.\n\nWhich approach fits?', 'pick': 1,
       'correct': [opt(AV['abac'], 'Separates rule-writing from tagging, and covers new tagged tables automatically.')],
       'distractors': [opt(AV['tbl'], 'Every new table needs its own setup by its owner.'),
                       opt(AV['grant'], 'Grants privileges; it doesn’t filter or mask.'),
                       opt(AV['view'], 'A new view for every table, maintained by hand.'),
                       opt(AV['filter'], 'Set table by table, with no use of the stewards’ tags.')]},
    ], setting=['Unity Catalog'], rev=1))
  EVIDENCE['dea-7-4-abac-vs-table'] = [(0, r'table owners cannot override, modify, or remove them'), (0, r'Managed by table owners, who can modify or remove filters and masks'),
    (0, r'New tagged tables are covered automatically'), (0, r'Each table must be configured individually'), (0, r'`SHOW EFFECTIVE POLICIES`'),
    (0, r'`ALTER TABLE \.\.\. SET ROW FILTER`'), (0, r'Each table has strict, specific logic that doesn\'t generalize'),
    (0, r'without a centralized tag system'), (0, r'policy authors define rules, and data stewards classify data with tags')]

  # ---------- 7.2 ownership and MANAGE ----------
  C.append(concept('dea-7-2-ownership-manage', '7', '7.2', 50, 'Ownership and the MANAGE privilege',
    [{'title': 'Manage privileges in Unity Catalog', 'url': G + '/manage-privileges/'}],
    [
      {'id': 'r1', 'type': 'basic', 'prompt': 'In Unity Catalog, who can grant privileges on a table?', 'answer': 'Its owner, its catalog’s or schema’s owner, a holder of `MANAGE` on it, or a metastore admin', 'why': 'Owners hold all privileges and can pass on `MANAGE` so others can manage grants.'},
      {'id': 'r2', 'type': 'basic', 'prompt': 'In Unity Catalog, which privilege lets someone who isn’t the owner manage grants on an object?', 'answer': '`MANAGE`', 'why': 'The owner can grant it to other users.'},
      {'id': 'r3', 'type': 'basic', 'prompt': 'In Unity Catalog, what access does a new user have to data in a metastore?', 'answer': 'None until it’s granted', 'why': 'Account, workspace and metastore admins have default privileges to start managing access.'},
      {'id': 'r4', 'type': 'basic', 'prompt': 'In Unity Catalog, which privileges does an object’s owner hold on it?', 'answer': 'All of them, including granting them to others', 'why': 'Every securable object has exactly one owner.'},
      {'id': 'r5', 'type': 'code', 'prompt': 'In Unity Catalog, take back the `contractors` group’s read access to `payroll`.', 'lang': 'sql', 'code': '{{gap}} SELECT\n  ON TABLE finance.gold.payroll\n  FROM `contractors`;', 'answer': 'REVOKE', 'why': '`REVOKE ... FROM` mirrors `GRANT ... TO`.'},
    ], setting=['Unity Catalog'], rev=1))
  EVIDENCE['dea-7-2-ownership-manage'] = [(0, r'Initially, users have no access to data in a metastore'), (0, r'All securable objects in Unity Catalog have an owner'),
    (0, r'Object owners have all privileges on that object, including the ability to grant privileges to other principals'),
    (0, r'Owners can grant other users the `MANAGE` privilege on the object'), (0, r'The owner of the catalog or schema that contains the object'),
    (0, r'A user with the `MANAGE` privilege on the object'), (0, r'A metastore admin'), (0, r'REVOKE'), (0, r'FROM')]
  return C

CHUNKS = [chunk1, chunk2, chunk3, chunk4]
