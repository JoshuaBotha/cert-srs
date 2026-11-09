# Cert SRS content: exam blueprint, the 10 sample concepts and the milestone 3 batch (batch_m3.py),
# written against the August 2026 guide and docs read 2026-11-06.
import json, os, re, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
GUIDE, VERIFIED = '2026-08-06', '2026-11-06'

exam = {
  'name': 'Databricks Certified Data Engineer Associate', 'code': 'databricks-dea',
  'guideDate': GUIDE, 'examPublished': '2026-05-04',
  'guideUrl': 'https://www.databricks.com/sites/default/files/2026-10/Databricks-Certified-Data-Engineer-Associate-Exam-Guide-August-2026.pdf',
  'format': {'scored': 45, 'unscoredMax': 10, 'minutes': 90, 'type': 'multiple choice', 'code': 'SQL where possible, otherwise Python'},
  'domains': [
    {'n': '1', 'name': 'Databricks Intelligence Platform', 'weight': 0.06, 'objectives': [
      {'code': '1.1', 'text': 'Understand the core components of the Databricks Platform, such as its architecture, Delta Lake, and Unity Catalog.'},
      {'code': '1.2', 'text': 'Understand compute services, their characteristics, limitations and cost models, and pick the right one for each workload.'}]},
    {'n': '2', 'name': 'Data Ingestion and Loading', 'weight': 0.21, 'objectives': [
      {'code': '2.1', 'text': 'Enable and detail batch, streaming and incremental ingestion patterns, from local files and Lakeflow Connect standard and managed connectors.'},
      {'code': '2.2', 'text': 'Use COPY INTO to incrementally load files from cloud object storage into Unity Catalog tables.'},
      {'code': '2.3', 'text': 'Use Auto Loader with schema enforcement and schema evolution to land data into Unity Catalog tables.'},
      {'code': '2.4', 'text': 'Configure Lakeflow Connect to reliably ingest data from enterprise sources into Unity Catalog tables.'},
      {'code': '2.5', 'text': 'Use JDBC/ODBC or REST clients in notebooks to land data in cloud storage or Unity Catalog tables, scheduled with Lakeflow Jobs.'},
      {'code': '2.6', 'text': 'Prioritize between Auto Loader, Lakeflow Connect, partner connectors and other ingestion methods by technical requirements.'},
      {'code': '2.7', 'text': 'Ingest semi-structured and unstructured data, such as nested JSON, into Unity Catalog Delta tables.'}]},
    {'n': '3', 'name': 'Data Transformation and Modeling', 'weight': 0.22, 'objectives': [
      {'code': '3.1', 'text': 'Clean bronze data with PySpark/SQL (nulls, data types) and write silver tables.'},
      {'code': '3.2', 'text': 'Combine DataFrames with inner, left, broadcast, multi-key and cross joins, union and union all.'},
      {'code': '3.3', 'text': 'Add, drop, split and rename columns, filter rows and explode arrays.'},
      {'code': '3.4', 'text': 'Deduplicate and aggregate DataFrames: count, approximate count distinct, mean, summary.'},
      {'code': '3.5', 'text': 'Understand basic tuning parameters (shuffle partitions, parallelism, memory, broadcast threshold) and re-measure.'},
      {'code': '3.6', 'text': 'Understand and build gold-layer objects: materialized views, views, streaming tables and tables in Unity Catalog.'},
      {'code': '3.7', 'text': 'Apply data quality checks and validation rules for reliable silver and gold datasets.'}]},
    {'n': '4', 'name': 'Working with Lakeflow Jobs', 'weight': 0.16, 'objectives': [
      {'code': '4.1', 'text': 'Implement control flows (retries, branching, looping) with Lakeflow Jobs.'},
      {'code': '4.2', 'text': 'Configure notebook, SQL query, dashboard and pipeline tasks and their dependencies in the task graph.'},
      {'code': '4.3', 'text': 'Implement job schedules with an understanding of trigger types: scheduled, file arrival and table update.'},
      {'code': '4.4', 'text': 'Choose between time-based and data-driven triggers based on data availability and pipeline dependencies.'}]},
    {'n': '5', 'name': 'Implementing CI/CD', 'weight': 0.10, 'objectives': [
      {'code': '5.1', 'text': 'Work with branches, commits, pushes and pull requests in Databricks Git folders.'},
      {'code': '5.2', 'text': 'Use Declarative Automation Bundle variables and overrides to promote one codebase across dev, test and prod.'},
      {'code': '5.3', 'text': 'Deploy Declarative Automation Bundles to package and promote jobs, pipelines and other assets across environments.'},
      {'code': '5.4', 'text': 'Use the Databricks CLI to validate, deploy and manage bundles in automated CI/CD workflows.'}]},
    {'n': '6', 'name': 'Troubleshooting, Monitoring, and Optimization', 'weight': 0.10, 'objectives': [
      {'code': '6.1', 'text': 'Spot job performance trends in the Lakeflow Jobs run history against historical baselines.'},
      {'code': '6.2', 'text': 'Monitor pipeline health in the Lakeflow Jobs UI: statuses, task graphs, run times and failure rates.'},
      {'code': '6.3', 'text': 'Identify skew, shuffling and disk spilling from stage-level metrics in the Spark UI.'},
      {'code': '6.4', 'text': 'Understand the features of liquid clustering and predictive optimization.'},
      {'code': '6.5', 'text': 'Diagnose cluster startup failures, library conflicts and out-of-memory issues.'}]},
    {'n': '7', 'name': 'Governance and Security', 'weight': 0.15, 'objectives': [
      {'code': '7.1', 'text': 'Differentiate managed and external tables in Unity Catalog and create, modify, delete and convert them.'},
      {'code': '7.2', 'text': 'Configure access with GRANT, REVOKE and DENY for users, groups and service principals at the right level.'},
      {'code': '7.3', 'text': 'Understand column-level masking and row-level security to restrict data by user group.'},
      {'code': '7.4', 'text': 'Understand Unity Catalog ABAC policies for central row filtering and column masking.'}]},
  ]}

def opt(text, why): return {'text': text, 'why': why}
def concept(cid, domain, obj, order, title, sources, recall, scenario=None, diagrams=None, setting=None, rev=None):
  c = {'setting': setting or SETTING[cid], 'domain': domain, 'objective': obj, 'order': order, 'title': title, 'exam': 'databricks-dea',
       'status': 'live', 'rev': REV.get(cid, rev or 2), 'guide': GUIDE, 'lastVerified': VERIFIED, 'sources': sources,
       'recall': {'variants': recall}, 'scenario': {'variants': scenario} if scenario else None}
  if diagrams: c['diagrams'] = diagrams
  return cid, c

D = 'https://docs.databricks.com'
# Card rule: every prompt names its setting (product or feature area) unless the setting is the answer.
REV = {k: 3 for k in ['dea-2-2-copy-into-idempotent', 'dea-2-3-autoloader-schema-evolution', 'dea-3-6-streaming-table-vs-mv',
  'dea-3-7-expectations', 'dea-7-2-usage-privileges', 'dea-7-3-masks-and-filters']}
SETTING = {
  'dea-1-2-compute-choice': ['compute', 'Lakeflow Jobs'], 'dea-2-2-copy-into-idempotent': ['COPY INTO'],
  'dea-2-3-autoloader-schema-evolution': ['Auto Loader'], 'dea-3-6-streaming-table-vs-mv': ['Lakeflow Declarative Pipeline'],
  'dea-3-7-expectations': ['Lakeflow Declarative Pipeline'], 'dea-4-4-job-triggers': ['Lakeflow Jobs'],
  'dea-5-2-bundle-variables': ['Declarative Automation Bundle'], 'dea-6-3-skew-vs-spill': ['Spark'],
  'dea-7-2-usage-privileges': ['Unity Catalog'], 'dea-7-3-masks-and-filters': ['Unity Catalog'],
}
C = []

# 1.2 compute choice
C.append(concept('dea-1-2-compute-choice', '1', '1.2', 1, 'Choosing compute for a workload',
  [{'title': 'Compute selection recommendations', 'url': D + '/aws/en/compute/choose-compute'}],
  [
    {'id': 'r1', 'type': 'decision', 'prompt': 'A BI dashboard runs short SQL queries on gold tables every few minutes in office hours, and nobody wants to manage clusters. Which compute should serve it?', 'answer': 'A serverless SQL warehouse', 'why': 'It’s built for SQL analytics and BI, starts in seconds and scales with concurrent queries.'},
    {'id': 'r2', 'type': 'comparison', 'prompt': 'Classic jobs compute or classic all-purpose compute: which one is created for a run, ends when the run ends, and can’t be restarted?', 'answer': 'Classic jobs compute', 'why': 'The job scheduler creates it per run; all-purpose compute is for interactive work and isn’t recommended for production jobs.'},
    {'id': 'r3', 'type': 'basic', 'prompt': 'For most automated Lakeflow Jobs tasks, which compute does Databricks recommend first?', 'answer': 'Serverless compute for jobs', 'why': 'Fewer settings, faster start-up, automatic scaling and lower cost; classic jobs compute is for settings serverless lacks.'},
    {'id': 'r4', 'type': 'decision', 'prompt': 'A Lakeflow Jobs task runs PySpark on a schedule and needs a GPU instance type and an init script, which serverless doesn’t offer. Which compute should it use?', 'answer': 'Classic jobs compute', 'why': 'Classic jobs compute takes custom cluster settings; all-purpose compute isn’t optimized for automated workloads.'},
  ],
  [
    {'id': 's1', 'stem': 'A finance team’s Databricks dashboard refreshes from gold tables every 15 minutes during office hours. Queries are short SQL, load spikes at month-end, and the team wants nothing to tune or restart.\n\nWhich compute should back the dashboard?', 'pick': 1,
     'correct': [opt('A serverless SQL warehouse', 'Built for BI and SQL: it starts in seconds and scales out for the month-end spike without cluster management.')],
     'distractors': [opt('Serverless compute for jobs', 'Meant for automated job tasks, not for serving interactive dashboard queries.'),
                     opt('A classic all-purpose cluster', 'Needs sizing and restarts, and isn’t optimized for many concurrent SQL readers.'),
                     opt('A classic jobs compute cluster', 'Created per job run and terminated after it, so it can’t serve a dashboard.'),
                     opt('A single-node all-purpose cluster', 'Sized for light development work; it can’t scale for month-end concurrency.')]},
    {'id': 's2', 'stem': 'A nightly Lakeflow Jobs task runs a PySpark notebook that cleans bronze data into silver. It needs no special libraries or instance types, and the team wants the fewest settings to maintain.\n\nWhich compute should the task use?', 'pick': 1,
     'correct': [opt('Serverless compute for jobs', 'Databricks’ default recommendation for automated tasks: no cluster settings, fast start-up and automatic scaling.')],
     'distractors': [opt('A classic all-purpose cluster', 'Kept for interactive work; Databricks advises against it for production jobs.'),
                     opt('A serverless SQL warehouse', 'Runs SQL, not a PySpark notebook task.'),
                     opt('A classic jobs compute cluster', 'Works, but adds cluster settings to maintain that this task doesn’t need.'),
                     opt('A single-node all-purpose cluster', 'An interactive development cluster that doesn’t scale for a production ETL run.')]},
    {'id': 's3', 'stem': 'A nightly Lakeflow Jobs task runs a PySpark notebook that needs a GPU instance type and an init script, and neither is available on serverless.\n\nWhich compute should the task use?', 'pick': 1,
     'correct': [opt('A classic jobs compute cluster', 'Takes custom instance types and init scripts, and is created and torn down with each run.')],
     'distractors': [opt('Serverless compute for jobs', 'Its settings are managed by Databricks, so the GPU type and init script aren’t available.'),
                     opt('A classic all-purpose cluster', 'Could run it, but stays up between runs and isn’t optimized for automated jobs.'),
                     opt('A serverless SQL warehouse', 'Runs SQL only; it can’t run a PySpark notebook on GPUs.'),
                     opt('A single-node all-purpose cluster', 'An interactive cluster for light development, not scheduled GPU work.')]},
  ]))

# 2.2 COPY INTO
C.append(concept('dea-2-2-copy-into-idempotent', '2', '2.2', 2, 'COPY INTO is idempotent',
  [{'title': 'COPY INTO (SQL reference)', 'url': D + '/en/sql/language-manual/delta-copy-into'},
   {'title': 'Common data loading patterns using COPY INTO', 'url': D + '/en/ingestion/copy-into/examples.html'}],
  [
    {'id': 'r1', 'type': 'basic', 'prompt': 'A `COPY INTO` command is re-run on a folder where most files were already loaded. What happens to those files?', 'answer': 'They’re skipped; only new files load', 'why': 'COPY INTO tracks loaded files, so re-runs are idempotent, even if a loaded file was modified since.'},
    {'id': 'r2', 'type': 'code', 'prompt': 'In `COPY INTO`, reload every file, including ones already loaded.', 'lang': 'sql', 'code': "COPY INTO main.bronze.orders\nFROM 's3://acme-landing/orders/'\nFILEFORMAT = JSON\nCOPY_OPTIONS ('{{gap}}' = 'true');", 'answer': 'force', 'why': '`force` set to true turns idempotency off, so files load whether or not they loaded before.'},
    {'id': 'r3', 'type': 'code', 'prompt': 'In `COPY INTO`, let new columns in the incoming files evolve the target table.', 'lang': 'sql', 'code': "COPY INTO lake.raw.clicks\nFROM 's3://web-drop/clicks/'\nFILEFORMAT = PARQUET\nCOPY_OPTIONS ('{{gap}}' = 'true');", 'answer': 'mergeSchema', 'why': 'In `COPY_OPTIONS`, `mergeSchema` evolves the target table. The `FORMAT_OPTIONS` one only merges schemas across the source files.', 'src': 1},
    {'id': 'r4', 'type': 'cloze', 'text': 'COPY INTO is a retryable, {{gap}} operation: files already loaded from the source are skipped.', 'answer': 'idempotent', 'why': 'Re-running it doesn’t duplicate rows, which makes it safe to schedule and retry.'},
  ]))

# 2.3 Auto Loader schema evolution
EV = {k: '`schemaEvolutionMode` set to `' + m + '`' for k, m in {'add': 'addNewColumns', 'rescue': 'rescue', 'fail': 'failOnNewColumns', 'none': 'none', 'widen': 'addNewColumnsWithTypeWidening'}.items()}
C.append(concept('dea-2-3-autoloader-schema-evolution', '2', '2.3', 3, 'Auto Loader schema evolution modes',
  [{'title': 'Configure schema inference and evolution in Auto Loader', 'url': D + '/ingestion/auto-loader/schema.html'}],
  [
    {'id': 'r1', 'type': 'basic', 'prompt': 'With no schema provided, what is Auto Loader’s default `cloudFiles.schemaEvolutionMode`?', 'answer': '`addNewColumns`', 'why': 'The stream stops on a new column after adding it to the schema; a restart continues with it.'},
    {'id': 'r2', 'type': 'code', 'prompt': 'Turn on Auto Loader schema inference and evolution.', 'lang': 'python', 'code': '(spark.readStream\n  .format("cloudFiles")\n  .option("cloudFiles.format", "json")\n  .option("cloudFiles.{{gap}}",\n    "/Volumes/main/chk/events")\n  .load("/Volumes/main/raw/events"))', 'answer': 'schemaLocation', 'why': 'Auto Loader stores the inferred schema and its changes under `cloudFiles.schemaLocation`.'},
    {'id': 'r3', 'type': 'symptom', 'prompt': 'An Auto Loader stream fails with `UnknownFieldException` the first time a new JSON field appears. No evolution mode was set. What happens when it restarts?', 'answer': 'It continues, with the new column in the schema', 'why': 'In the default `addNewColumns` mode the schema is updated before the stream fails, so a restart picks it up.'},
    {'id': 'r4', 'type': 'comparison', 'prompt': 'In Auto Loader, `rescue` or `none`: which schema evolution mode keeps the data from new columns instead of dropping it?', 'answer': '`rescue`, into `_rescued_data`', 'why': '`none` ignores new columns unless a rescued data column is set; `rescue` always records them.'},
  ],
  [
    {'id': 's1', 'stem': 'An Auto Loader stream lands a partner’s JSON files in a bronze table. The files gain new fields a few times a month. Analysts want each new field to appear as a column in the bronze table automatically, and a short stream restart is acceptable.\n\nWhich Auto Loader setting fits?', 'pick': 1,
     'correct': [opt(EV['add'], 'Adds new columns to the schema; the stream stops once and resumes with them on restart.')],
     'distractors': [opt(EV['rescue'], 'Never evolves the schema, so new fields stay in `_rescued_data` instead of becoming columns.'),
                     opt(EV['fail'], 'Stops the stream until someone updates the schema by hand.'),
                     opt(EV['none'], 'Ignores new columns, so the fields never appear.'),
                     opt(EV['widen'], 'Also adds columns, but its point is widening types, and it’s in Public Preview.')]},
    {'id': 's2', 'stem': 'An Auto Loader stream lands a partner’s JSON files in a bronze table. The files gain new fields a few times a month. The bronze schema must stay fixed for a downstream contract, the stream must never stop for schema changes, and no incoming values may be lost.\n\nWhich Auto Loader setting fits?', 'pick': 1,
     'correct': [opt(EV['rescue'], 'Keeps the schema fixed and never fails; new fields are kept in `_rescued_data`.')],
     'distractors': [opt(EV['add'], 'Changes the schema and stops the stream once per new column.'),
                     opt(EV['fail'], 'Stops the stream on every new column.'),
                     opt(EV['none'], 'Keeps running, but drops new fields unless a rescued data column is set.'),
                     opt(EV['widen'], 'Evolves the schema, which breaks the fixed contract.')]},
    {'id': 's3', 'stem': 'An Auto Loader stream lands a partner’s JSON files in a bronze table, and the files must match an agreed schema exactly. Any unexpected field should stop ingestion until an engineer reviews it and updates the schema.\n\nWhich Auto Loader setting fits?', 'pick': 1,
     'correct': [opt(EV['fail'], 'Fails on a new column and stays stopped until the schema is updated or the file removed.')],
     'distractors': [opt(EV['add'], 'Adds the field to the schema automatically, so no review happens.'),
                     opt(EV['rescue'], 'Keeps running and stores the field in `_rescued_data`, so nothing stops.'),
                     opt(EV['none'], 'Keeps running and ignores the field, so nothing stops.'),
                     opt(EV['widen'], 'Adds the field and widens types automatically, so no review happens.')]},
  ]))

# 3.6 streaming table vs materialized view
TO = {'st': 'A streaming table in the pipeline', 'mv': 'A materialized view in the pipeline', 'tv': 'A temporary view in the pipeline', 'uv': 'A standard view in Unity Catalog', 'tbl': 'A Delta table rebuilt by INSERT OVERWRITE'}
C.append(concept('dea-3-6-streaming-table-vs-mv', '3', '3.6', 4, 'Streaming table, materialized view or view',
  [{'title': 'Transform data with pipelines', 'url': D + '/delta-live-tables/load-and-transform.html'}],
  [
    {'id': 'r1', 'type': 'comparison', 'prompt': 'In a Lakeflow Declarative Pipeline, streaming table or materialized view: which assumes an append-only source and processes each record once?', 'answer': 'Streaming table', 'why': 'Streaming tables suit ingestion of continuously growing data; updates and deletes upstream break that assumption.'},
    {'id': 'r2', 'type': 'decision', 'prompt': 'In a Lakeflow Declarative Pipeline, a gold table sums revenue by region from a silver table that receives updates and deletes. Streaming table or materialized view?', 'answer': 'Materialized view', 'why': 'A materialized view keeps a batch-style query current, reprocessing only changed data when it can.'},
    {'id': 'r3', 'type': 'code', 'prompt': 'In a Lakeflow Declarative Pipeline, ingest new files incrementally.', 'lang': 'sql', 'code': "CREATE OR REFRESH {{gap}}\n  bronze_events\nAS SELECT * FROM STREAM read_files(\n  '/Volumes/main/raw/events',\n  format => 'json');", 'answer': 'STREAMING TABLE', 'why': 'A streaming table reads each new file once; `STREAM` marks the source as incremental.'},
    {'id': 'r4', 'type': 'code', 'prompt': 'In a Lakeflow Declarative Pipeline, precompute a daily total that stays correct when orders are corrected.', 'lang': 'sql', 'code': 'CREATE OR REFRESH {{gap}}\n  gold_daily_sales AS\nSELECT order_date,\n  sum(amount) AS total\nFROM silver_orders\nGROUP BY order_date;', 'answer': 'MATERIALIZED VIEW', 'why': 'The aggregate must reflect updates to its source, which a materialized view handles.'},
  ],
  [
    {'id': 's1', 'stem': 'Clickstream JSON files land in a volume every few minutes and are never changed once written. A Lakeflow Declarative Pipeline needs a bronze table that reads each file once, with low latency.\n\nWhat should the pipeline define?', 'pick': 1,
     'correct': [opt(TO['st'], 'Processes each appended record exactly once, which suits continuous ingestion.')],
     'distractors': [opt(TO['mv'], 'Built for queries over changing data; more than this append-only ingest needs.'),
                     opt(TO['tv'], 'Not materialized, so nothing outside the pipeline can read it as a bronze table.'),
                     opt(TO['uv'], 'Recomputes on every query and doesn’t ingest anything incrementally.'),
                     opt(TO['tbl'], 'Rewrites everything on each run instead of reading only new files.')]},
    {'id': 's2', 'stem': 'In a Lakeflow Declarative Pipeline, a gold table must show revenue by region from a silver orders table that is regularly corrected with updates and deletes. BI users need the totals precomputed so reads are fast.\n\nWhat should the pipeline define?', 'pick': 1,
     'correct': [opt(TO['mv'], 'Keeps the aggregate current over changing data, incrementally where possible, and stores the result.')],
     'distractors': [opt(TO['st'], 'Assumes an append-only source, so upstream updates and deletes aren’t handled.'),
                     opt(TO['tv'], 'Exists only inside the pipeline, so BI users can’t query it.'),
                     opt(TO['uv'], 'Recomputes the aggregate on every query, so reads aren’t fast.'),
                     opt(TO['tbl'], 'Works, but recomputes everything on every run with no incremental refresh.')]},
    {'id': 's3', 'stem': 'A complex join is only an intermediate step inside one Lakeflow Declarative Pipeline. No query outside the pipeline reads it, and the team wants to avoid paying to store it.\n\nWhat should the pipeline define?', 'pick': 1,
     'correct': [opt(TO['tv'], 'Organizes the pipeline’s logic without storing anything, and is visible only inside it.')],
     'distractors': [opt(TO['mv'], 'Stores its results, which the team wants to avoid for an internal step.'),
                     opt(TO['st'], 'A stored table meant for ingesting append-only data, not an internal step.'),
                     opt(TO['uv'], 'Publishes the step to Unity Catalog, where nobody needs it.'),
                     opt(TO['tbl'], 'Stores and rewrites a full table for a step nobody reads.')]},
  ]))

# 3.7 expectations
EX = {'drop': '`ON VIOLATION DROP ROW`', 'fail': '`ON VIOLATION FAIL UPDATE`', 'warn': '`EXPECT` with no `ON VIOLATION`', 'check': 'A `CHECK` constraint on the table', 'where': 'A `WHERE` clause in the query'}
C.append(concept('dea-3-7-expectations', '3', '3.7', 5, 'Pipeline expectation actions',
  [{'title': 'Manage data quality with pipeline expectations', 'url': D + '/aws/en/ldp/expectations'}],
  [
    {'id': 'r1', 'type': 'basic', 'prompt': 'A Lakeflow Declarative Pipeline expectation has no `ON VIOLATION` clause. What happens to rows that fail it?', 'answer': 'They’re kept and counted in the metrics', 'why': 'Warn is the default action: invalid rows reach the target and violations are logged.'},
    {'id': 'r2', 'type': 'code', 'prompt': 'In a Lakeflow Declarative Pipeline expectation, discard bad rows and keep the update running.', 'lang': 'sql', 'code': 'CREATE OR REFRESH STREAMING TABLE\n  silver_payments (\n  CONSTRAINT valid_amount\n    EXPECT (amount > 0)\n    ON VIOLATION {{gap}}\n) AS SELECT *\n  FROM STREAM(bronze_payments);', 'answer': 'DROP ROW', 'why': 'Invalid rows are dropped before the write, and the drop count is logged.'},
    {'id': 'r3', 'type': 'code', 'prompt': 'In a Lakeflow Declarative Pipeline expectation, stop the update on the first bad row.', 'lang': 'sql', 'code': 'CREATE OR REFRESH STREAMING TABLE\n  silver_shipments (\n  CONSTRAINT has_order\n    EXPECT (order_id IS NOT NULL)\n    ON VIOLATION {{gap}}\n) AS SELECT *\n  FROM STREAM(bronze_shipments);', 'answer': 'FAIL UPDATE', 'why': 'The update fails and its table change is rolled back; someone must fix the data first.'},
    {'id': 'r4', 'type': 'symptom', 'prompt': 'A Lakeflow Declarative Pipeline update stops, its table change is rolled back, and the error names a violated expectation. Which action was set?', 'answer': '`ON VIOLATION FAIL UPDATE`', 'why': 'Fail is the only action that stops the update; warn and drop let it finish.'},
  ],
  [
    {'id': 's1', 'stem': 'A Lakeflow Declarative Pipeline loads sensor readings into silver, and some arrive with a null `device_id`. Those rows are useless downstream, but one bad row must not stop the pipeline, and the team wants to see how many were removed.\n\nWhich expectation setup fits?', 'pick': 1,
     'correct': [opt(EX['drop'], 'Drops the invalid rows, keeps the update running and logs how many were dropped.')],
     'distractors': [opt(EX['fail'], 'Stops the whole update on the first null, which the team wants to avoid.'),
                     opt(EX['warn'], 'Keeps the useless rows in the target.'),
                     opt(EX['check'], 'Makes the write fail when a row violates it, stopping the update.'),
                     opt(EX['where'], 'Removes the rows, but records no data quality metrics.')]},
    {'id': 's2', 'stem': 'A Lakeflow Declarative Pipeline loads ledger rows into silver. A null `account_id` means an upstream system is broken. When that happens, no partial data may reach silver until someone investigates.\n\nWhich expectation setup fits?', 'pick': 1,
     'correct': [opt(EX['fail'], 'Fails the update and rolls back its change, so no partial data lands.')],
     'distractors': [opt(EX['drop'], 'Lets the update finish with the bad rows removed, hiding the outage.'),
                     opt(EX['warn'], 'Writes the bad rows to silver and only counts them.'),
                     opt(EX['where'], 'Silently filters the rows out, so nobody learns of the outage.'),
                     opt(EX['check'], 'Enforced on the table, outside the pipeline’s data quality metrics.')]},
    {'id': 's3', 'stem': 'A Lakeflow Declarative Pipeline loads orders into silver, and a new rule flags orders with a missing coupon code. The team doesn’t yet know how often it fires and must keep every row while they watch the counts.\n\nWhich expectation setup fits?', 'pick': 1,
     'correct': [opt(EX['warn'], 'Warn is the default: every row is kept and the violations are counted.')],
     'distractors': [opt(EX['drop'], 'Removes the flagged orders, but every row must be kept.'),
                     opt(EX['fail'], 'Stops the pipeline as soon as one order lacks a coupon.'),
                     opt(EX['where'], 'Removes the flagged rows and records nothing.'),
                     opt(EX['check'], 'Rejects writes that violate it, so rows wouldn’t be kept.')]},
  ]))

# 4.4 triggers
TR = {'tu': 'A table update trigger on the source table', 'sch': 'A scheduled trigger at a fixed time', 'fa': 'A file arrival trigger on the storage location', 'cont': 'A continuous trigger on the job', 'man': 'A manual trigger started by an operator'}
C.append(concept('dea-4-4-job-triggers', '4', '4.4', 6, 'Time-based or data-driven job triggers',
  [{'title': 'Automate jobs with schedules and triggers', 'url': D + '/aws/en/jobs/triggers'},
   {'title': 'Trigger jobs when source tables are updated', 'url': D + '/aws/en/jobs/trigger-table-update'}],
  [
    {'id': 'r1', 'type': 'decision', 'prompt': 'A job in Lakeflow Jobs should run whenever another team’s pipeline updates `main.silver.orders`. Which trigger type?', 'answer': 'Table update', 'why': 'It watches Unity Catalog tables and starts a run after they change, with no cluster waiting.', 'src': 1},
    {'id': 'r2', 'type': 'decision', 'prompt': 'A job in Lakeflow Jobs should run when new files land in a Unity Catalog volume. Which trigger type?', 'answer': 'File arrival', 'why': 'It monitors a Unity Catalog storage location and starts a run when new files appear.'},
    {'id': 'r3', 'type': 'basic', 'prompt': 'A job in Lakeflow Jobs reads two upstream tables. How should its table update trigger be set so it waits until both have changed?', 'answer': 'Run when all monitored tables are updated', 'why': 'A table update trigger can fire on any one table or only once all monitored tables are updated.', 'src': 1},
    {'id': 'r4', 'type': 'comparison', 'prompt': 'In Lakeflow Jobs, scheduled or table update trigger: which one can start runs that find no new data?', 'answer': 'Scheduled', 'why': 'A schedule fires on time whether or not data changed; a table update trigger fires only after a change.'},
  ],
  [
    {'id': 's1', 'stem': 'A gold job in Lakeflow Jobs must run as soon as another team’s pipeline finishes writing `sales.silver.orders`. That pipeline finishes at a different time every day, and the gold team doesn’t own it or want idle compute.\n\nWhich trigger should the gold job use?', 'pick': 1,
     'correct': [opt(TR['tu'], 'Starts a run after the table changes, whenever that is, with no compute waiting.')],
     'distractors': [opt(TR['sch'], 'Either runs before the data is ready or waits long after it lands.'),
                     opt(TR['fa'], 'Watches files in a storage location, not commits to a Unity Catalog table.'),
                     opt(TR['cont'], 'Keeps the job running all the time, which is the idle compute to avoid.'),
                     opt(TR['man'], 'Needs a person to notice the update every day.')]},
    {'id': 's2', 'stem': 'A gold job in Lakeflow Jobs must publish a regulatory report at 06:00 every weekday, using whatever data has arrived by then. Late data goes into the next day’s report.\n\nWhich trigger should the job use?', 'pick': 1,
     'correct': [opt(TR['sch'], 'The deadline is a fixed time, so a time-based schedule fits.')],
     'distractors': [opt(TR['tu'], 'Runs when data changes, which may miss or overshoot the 06:00 deadline.'),
                     opt(TR['fa'], 'Runs when files arrive, not at the deadline.'),
                     opt(TR['cont'], 'Reruns the job back to back instead of once at 06:00.'),
                     opt(TR['man'], 'Depends on someone starting it on time every weekday.')]},
    {'id': 's3', 'stem': 'A mobile app uploads scanned invoices as PDFs into a Unity Catalog volume at unpredictable times. A job in Lakeflow Jobs must process each upload within minutes, without polling and without runs that find nothing.\n\nWhich trigger should the job use?', 'pick': 1,
     'correct': [opt(TR['fa'], 'Starts a run only when new files appear in the monitored location.')],
     'distractors': [opt(TR['sch'], 'A schedule is polling: many runs would find no new files.'),
                     opt(TR['tu'], 'Watches table commits, but the invoices arrive as files in a volume.'),
                     opt(TR['cont'], 'Keeps a run going even when nothing has been uploaded.'),
                     opt(TR['man'], 'Can’t react within minutes to unpredictable uploads.')]},
  ]))

# 5.2 bundle variables
C.append(concept('dea-5-2-bundle-variables', '5', '5.2', 7, 'Bundle variables and target overrides',
  [{'title': 'Substitutions and variables in Declarative Automation Bundles', 'url': D + '/dev-tools/bundles/variables'}],
  [
    {'id': 'r1', 'type': 'code', 'prompt': 'In a Declarative Automation Bundle’s `databricks.yml`, give the prod target its own value for `catalog`.', 'lang': 'yaml', 'code': 'targets:\n  dev:\n    default: true\n  prod:\n    {{gap}}:\n      catalog: prod_catalog', 'answer': 'variables', 'why': 'A `variables` mapping inside a target overrides the top-level default for that target.'},
    {'id': 'r2', 'type': 'basic', 'prompt': 'How do you reference a Declarative Automation Bundle variable named `warehouse_id` in `databricks.yml`?', 'answer': '`${var.warehouse_id}`', 'why': 'Custom variables are substituted with the `${var.<name>}` syntax.'},
    {'id': 'r3', 'type': 'basic', 'prompt': 'In a Declarative Automation Bundle, the variable `catalog` is set both in `BUNDLE_VAR_catalog` and under `targets.prod.variables`. Which value does `databricks bundle deploy -t prod` use?', 'answer': 'The `BUNDLE_VAR_catalog` value', 'why': 'Order: `--var`, then `BUNDLE_VAR_` variables, then variable-overrides.json, then target values, then the default.'},
    {'id': 'r4', 'type': 'cloze', 'text': 'Declarative Automation Bundle variables are resolved at {{gap}} time, so values that change per run belong in job parameters.', 'answer': 'deployment', 'why': 'The CLI substitutes them when you validate or deploy the bundle, not when a job runs.'},
  ]))

# 6.3 skew vs spill
SK = {'parts': 'Raise `spark.sql.shuffle.partitions`, or set it to `auto`', 'salt': 'Salt the hot key and aggregate in two passes', 'exec': 'Add more executors of the same size', 'fewer': 'Lower `spark.sql.shuffle.partitions` to run fewer tasks', 'bcast': 'Broadcast the smaller side of a join'}
C.append(concept('dea-6-3-skew-vs-spill', '6', '6.3', 8, 'Telling skew from spill in the Spark UI',
  [{'title': 'Skew and spill (Spark UI guide)', 'url': D + '/aws/en/optimizations/spark-ui-guide/long-spark-stage-page'}],
  [
    {'id': 'r1', 'type': 'symptom', 'prompt': 'In the Spark UI, a stage’s Summary Metrics show Max task duration is 40× the 75th percentile, and one task reads most of the shuffle data. Likely cause?', 'answer': 'Data skew', 'why': 'In a healthy stage the 75th percentile and Max are close; one oversized partition points to a hot key.'},
    {'id': 'r2', 'type': 'symptom', 'prompt': 'In the Spark UI, a stage shows spill on almost every task, and task durations are even. Likely cause?', 'answer': 'Partitions too big for execution memory', 'why': 'Spill means Spark ran short of execution memory and wrote to disk; it’s spread out, not one hot key.'},
    {'id': 'r3', 'type': 'basic', 'prompt': 'Which setting lets Spark pick the number of shuffle partitions from the query plan and input size?', 'answer': '`spark.sql.shuffle.partitions` = `auto`', 'why': 'Auto-optimized shuffle sizes partitions so they’re less likely to spill.'},
    {'id': 'r4', 'type': 'comparison', 'prompt': 'Does Spark’s adaptive query execution (AQE) skew handling cover skewed joins, skewed aggregations, or both?', 'answer': 'Joins only', 'why': 'AQE splits skewed partitions for sort-merge and shuffle-hash joins past its size thresholds; aggregations need a fix such as salting.'},
  ],
  [
    {'id': 's1', 'stem': 'A silver job slowed down. In the Spark UI, its longest stage shows spill on nearly every task, task durations are close together, and executors have spare cores.\n\nWhich change addresses the cause?', 'pick': 1,
     'correct': [opt(SK['parts'], 'Smaller partitions fit in execution memory, so tasks stop spilling.')],
     'distractors': [opt(SK['salt'], 'Fixes one hot key, but durations are even, so there’s no skew.'),
                     opt(SK['exec'], 'Each task still gets the same partition and memory, so it still spills.'),
                     opt(SK['fewer'], 'Makes each partition bigger, so spill gets worse.'),
                     opt(SK['bcast'], 'Removes a join shuffle, but nothing here points to the join.')]},
    {'id': 's2', 'stem': 'A silver job slowed down. In the Spark UI, its longest stage shows 199 tasks finish in seconds but one runs for 12 minutes, reading ten times the median shuffle data. The stage is a `groupBy` on `merchant_id`.\n\nWhich change addresses the cause?', 'pick': 1,
     'correct': [opt(SK['salt'], 'Spreads the hot merchant across many tasks, then combines the partial results.')],
     'distractors': [opt(SK['parts'], 'More partitions still send every row for that merchant to one task.'),
                     opt(SK['exec'], 'The one oversized task still runs alone on a single core.'),
                     opt(SK['fewer'], 'Bigger partitions make the skewed task even longer.'),
                     opt(SK['bcast'], 'There’s no join here; the slow step is an aggregation.')]},
    {'id': 's3', 'stem': 'A nightly Spark aggregation over 2 TB runs with `spark.sql.shuffle.partitions` set to 200. In the Spark UI, every shuffle task spills several gigabytes to disk, and task durations are uniform.\n\nWhich change is the cheapest first fix?', 'pick': 1,
     'correct': [opt(SK['parts'], '200 partitions is far too few for 2 TB; smaller partitions stop the spill.')],
     'distractors': [opt(SK['exec'], 'Costs more and leaves each task with the same oversized partition.'),
                     opt(SK['salt'], 'Durations are uniform, so there’s no hot key to spread.'),
                     opt(SK['fewer'], 'Makes partitions even larger, so each task spills more.'),
                     opt(SK['bcast'], 'This stage is an aggregation, not a join.')]},
  ]))

# 7.2 usage privileges (with an occlusion diagram of the hierarchy)
BOX = (150, 44)
LAB = {'metastore': (175, 10), 'catalog': (175, 84), 'schema': (175, 158), 'table': (10, 250), 'view': (175, 250), 'volume': (340, 250)}
NAMES = {'metastore': 'Metastore', 'catalog': 'Catalog', 'schema': 'Schema', 'table': 'Table', 'view': 'View', 'volume': 'Volume'}
def uc_svg():
  s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 310" font-family="Helvetica, Arial, sans-serif" font-size="23" font-weight="600">']
  cx = 175 + BOX[0] / 2
  for a, b in [('metastore', 'catalog'), ('catalog', 'schema')]:
    s.append(f'<line x1="{cx}" y1="{LAB[a][1] + BOX[1]}" x2="{cx}" y2="{LAB[b][1]}" stroke="#55605b" stroke-width="2"/>')
  s.append(f'<line x1="{cx}" y1="{LAB["schema"][1] + BOX[1]}" x2="{cx}" y2="226" stroke="#55605b" stroke-width="2"/>')
  s.append(f'<line x1="{10 + BOX[0] / 2}" y1="226" x2="{340 + BOX[0] / 2}" y2="226" stroke="#55605b" stroke-width="2"/>')
  for k in ['table', 'view', 'volume']:
    x = LAB[k][0] + BOX[0] / 2
    s.append(f'<line x1="{x}" y1="226" x2="{x}" y2="250" stroke="#55605b" stroke-width="2"/>')
  for k, (x, y) in LAB.items():
    s.append(f'<rect x="{x}" y="{y}" width="{BOX[0]}" height="{BOX[1]}" rx="8" fill="#ffffff" stroke="#1d2622" stroke-width="2"/>')
    s.append(f'<text x="{x + BOX[0] / 2}" y="{y + 30}" text-anchor="middle" fill="#1d2622">{NAMES[k]}</text>')
  s.append('</svg>')
  return ''.join(s)
UP = {'uc': 'USE CATALOG on the `sales` catalog', 'us': 'USE SCHEMA on the `sales.gold` schema', 'mod': 'MODIFY on the `daily_revenue` table', 'all': 'ALL PRIVILEGES on the `sales` catalog', 'selschema': 'SELECT on the `sales.gold` schema', 'browse': 'BROWSE on the `sales` catalog'}
C.append(concept('dea-7-2-usage-privileges', '7', '7.2', 9, 'Usage privileges: USE CATALOG and USE SCHEMA',
  [{'title': 'Unity Catalog permissions concepts', 'url': D + '/aws/en/data-governance/unity-catalog/access-control/permissions-concepts'},
   {'title': 'Unity Catalog securable objects', 'url': D + '/aws/en/data-governance/unity-catalog/securable-objects'}],
  [
    {'id': 'r1', 'type': 'basic', 'prompt': 'In Unity Catalog, an analyst has SELECT on `finance.reporting.revenue` but can’t query it. Which two privileges are missing?', 'answer': 'USE CATALOG on `finance` and USE SCHEMA on `finance.reporting`', 'why': 'Usage privileges on the parent catalog and schema are needed in addition to SELECT on the table.'},
    {'id': 'r2', 'type': 'cloze', 'text': 'To read a Unity Catalog table, a user needs USE CATALOG on its catalog, USE SCHEMA on its schema, and {{gap}} on the table.', 'answer': 'SELECT', 'why': 'All three are required; SELECT alone isn’t enough.'},
    {'id': 'r3', 'type': 'code', 'prompt': 'In Unity Catalog, `bi_readers` already has USE CATALOG on `sales`. Let them read one table.', 'lang': 'sql', 'code': 'GRANT {{gap}}\n  ON SCHEMA sales.silver\n  TO `bi_readers`;\nGRANT SELECT\n  ON TABLE sales.silver.orders\n  TO `bi_readers`;', 'answer': 'USE SCHEMA', 'why': 'USE SCHEMA lets them reach objects in the schema; it grants no data access by itself.'},
    {'id': 'r4', 'type': 'occlusion', 'diagram': 'uc', 'mask': 'schema', 'prompt': 'Name the hidden level in this Unity Catalog hierarchy.', 'answer': 'Schema', 'why': 'The namespace is catalog.schema.object under a metastore; USE SCHEMA is the usage privilege at this level.', 'src': 1},
    {'id': 'r5', 'type': 'occlusion', 'diagram': 'uc', 'mask': 'catalog', 'prompt': 'Name the hidden level in this Unity Catalog hierarchy.', 'answer': 'Catalog', 'why': 'The first level of catalog.schema.object; USE CATALOG is required before anything inside it can be used.', 'src': 1},
  ],
  [
    {'id': 's1', 'stem': 'In Unity Catalog, the `bi_readers` group has SELECT on `sales.gold.daily_revenue`, but their queries fail with a permission error. The table owner wants the smallest change that lets them read it.\n\nWhich grants are needed?', 'pick': 2,
     'correct': [opt(UP['uc'], 'Required to use anything inside the catalog, whatever is granted below it.'),
                 opt(UP['us'], 'Required to reach objects in the schema, in addition to USE CATALOG.')],
     'distractors': [opt(UP['mod'], 'Allows writing to the table, which reading doesn’t need.'),
                     opt(UP['all'], 'Far broader than needed; it covers every schema and table in the catalog.'),
                     opt(UP['selschema'], 'They already have SELECT on the table; the usage privileges are what’s missing.'),
                     opt(UP['browse'], 'Lets them see metadata, not read data in the table.')]},
    {'id': 's2', 'stem': 'In Unity Catalog, a new analyst must read every current and future table in `hr.reporting`, and nothing else. USE CATALOG on `hr` is already granted.\n\nWhich grants complete the access?', 'pick': 2,
     'correct': [opt('USE SCHEMA on the `hr.reporting` schema', 'Needed to reach any object in the schema.'),
                 opt('SELECT on the `hr.reporting` schema', 'Inherits to every current and future table in the schema.')],
     'distractors': [opt('SELECT on each table in `hr.reporting`', 'Covers today’s tables only; future tables would need new grants.'),
                     opt('ALL PRIVILEGES on the `hr` catalog', 'Grants far more than read access to one schema.'),
                     opt('MANAGE on the `hr.reporting` schema', 'Lets them manage grants and ownership, not read data.'),
                     opt('USE CATALOG on the `hr` catalog', 'Already granted; it doesn’t give access to the schema’s data.')]},
    {'id': 's3', 'stem': 'In Unity Catalog, the `auditors` group must read `ops.logs.access_events` and no other table. They already hold USE CATALOG on `ops` and USE SCHEMA on `ops.logs`.\n\nWhich grant gives least privilege?', 'pick': 1,
     'correct': [opt('SELECT on the `access_events` table', 'Grants read access to exactly this table, with the usage privileges already in place.')],
     'distractors': [opt('SELECT on the `ops.logs` schema', 'Inherits to every table in the schema, not just this one.'),
                     opt('SELECT on the `ops` catalog', 'Inherits to every table in every schema of the catalog.'),
                     opt('MODIFY on the `access_events` table', 'Allows writes, which auditors don’t need.'),
                     opt('ALL PRIVILEGES on the `access_events` table', 'Includes writing to the table as well as reading it.')]},
  ],
  {'uc': {'svg': uc_svg(), 'w': 500, 'h': 310, 'box': list(BOX), 'labels': {k: list(v) for k, v in LAB.items()}}}))

# 7.3 masks and row filters
C.append(concept('dea-7-3-masks-and-filters', '7', '7.3', 10, 'Column masks and row filters',
  [{'title': 'Column mask clause (SQL reference)', 'url': D + '/aws/en/sql/language-manual/sql-ref-syntax-ddl-column-mask'},
   {'title': 'ROW FILTER clause (SQL reference)', 'url': 'https://learn.microsoft.com/en-ca/azure/Databricks/sql/language-manual/sql-ref-syntax-ddl-row-filter'}],
  [
    {'id': 'r1', 'type': 'code', 'prompt': 'In Unity Catalog, make most readers see a redacted `national_id`.', 'lang': 'sql', 'code': 'ALTER TABLE hr.people.employees\n  ALTER COLUMN national_id\n  SET {{gap}} redact_id;', 'answer': 'MASK', 'why': 'The mask function runs as each row is fetched; its first argument is the masked column.'},
    {'id': 'r2', 'type': 'code', 'prompt': 'In Unity Catalog, hide EU rows from everyone outside `eu_analysts`.', 'lang': 'sql', 'code': "CREATE FUNCTION eu_only(region STRING)\n  RETURN is_account_group_member(\n    'eu_analysts') OR region <> 'EU';\n\nALTER TABLE sales.gold.orders\n  SET {{gap}} eu_only ON (region);", 'answer': 'ROW FILTER', 'why': 'The filter function returns a boolean per row; rows where it’s FALSE or NULL are hidden.', 'src': 1},
    {'id': 'r3', 'type': 'basic', 'prompt': 'A Unity Catalog row filter function returns NULL for a row. Does the reader see that row?', 'answer': 'No', 'why': 'Rows are filtered out when the function returns FALSE or NULL.', 'src': 1},
    {'id': 'r4', 'type': 'comparison', 'prompt': 'In Unity Catalog, column mask or row filter: which changes what a value looks like but keeps every row visible?', 'answer': 'Column mask', 'why': 'A mask rewrites one column per reader; a row filter decides which rows a reader sees.'},
    {'id': 'r5', 'type': 'basic', 'prompt': 'Inside a Unity Catalog mask or filter function, which function checks whether the reader belongs to an account group?', 'answer': '`is_account_group_member()`', 'why': 'It returns true when the user is a direct or indirect member of the named account group.'},
  ]))

# ---------- milestone 3 batch ----------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch_m3
for chunk in batch_m3.CHUNKS: C.extend(chunk(concept, opt))

# ---------- card-rule checks ----------
problems, notes = [], []
if len({cid for cid, _ in C}) != len(C): problems.append('duplicate concept ids')
if len({c['order'] for _, c in C}) != len(C): problems.append('duplicate order values')
def prose_fields(v):
  for k in ('prompt', 'text', 'stem', 'answer', 'why'):
    if k in v: yield k, v[k]
for cid, c in C:
  r = c['recall']['variants']; s = (c['scenario'] or {}).get('variants', [])
  if len(r) < 3: problems.append(f'{cid}: recall track has {len(r)} variants')
  if c['scenario'] and len(s) < 3: problems.append(f'{cid}: scenario track has {len(s)} variants')
  if len({v['id'] for v in r}) != len(r) or len({v['id'] for v in s}) != len(s): problems.append(f'{cid}: duplicate variant ids')
  for v in r:
    if v['type'] in ('cloze', 'code'):
      field = v['text'] if v['type'] == 'cloze' else v['code']
      if field.count('{{gap}}') != 1: problems.append(f'{cid}/{v["id"]}: needs exactly one gap')
    if v['type'] == 'occlusion' and v['mask'] not in c['diagrams'][v['diagram']]['labels']: problems.append(f'{cid}/{v["id"]}: bad mask')
    if v.get('src', 0) >= len(c['sources']): problems.append(f'{cid}/{v["id"]}: bad source index')
  for v in s:
    k = v['pick']
    if len(v['correct']) != k: problems.append(f'{cid}/{v["id"]}: pick {k} but {len(v["correct"])} correct')
    if not 4 <= len(v['distractors']) <= 6: problems.append(f'{cid}/{v["id"]}: distractor pool {len(v["distractors"])}')
    allo = v['correct'] + v['distractors']
    if any(not o.get('why') for o in allo): problems.append(f'{cid}/{v["id"]}: option without explanation')
    if any(re.search(r'all of the above|none of the above', o['text'], re.I) for o in allo): problems.append(f'{cid}/{v["id"]}: “of the above” option')
    L = [len(re.sub(r'`', '', o['text'])) for o in allo]
    ratio = max(L) / min(L)
    if ratio > 2.2: notes.append(f'{cid}/{v["id"]}: option length ratio {ratio:.1f}')
    if v.get('flip'):
      mate = next((x for x in s if x['id'] == v['flip']), None)
      if not mate or mate.get('flip') != v['id']: problems.append(f'{cid}/{v["id"]}: flip partner {v["flip"]} missing or not paired back')
      elif {o['text'] for o in v['correct']} == {o['text'] for o in mate['correct']}: problems.append(f'{cid}/{v["id"]}: flip pair has the same answer')
    texts = [o['text'] for o in allo]
    if len(set(texts)) != len(texts): problems.append(f'{cid}/{v["id"]}: duplicate option text')
  for v in r + s:
    for k, t in prose_fields(v):
      bare = re.sub(r'`[^`]*`', '', t)
      if "'" in bare or '"' in bare: problems.append(f'{cid}/{v["id"]}.{k}: straight quote in prose: {bare[:60]}')
  for v in r + s:
    q = v.get('prompt') or v.get('text') or v.get('stem') or ''
    if not v.get('settingIsAnswer') and not any(t.lower() in q.lower() for t in c['setting']):
      problems.append(f'{cid}/{v["id"]}: prompt doesn’t name its setting ({" / ".join(c["setting"])})')
  for v in r:
    for ln in (v.get('code') or '').split('\n'):
      if len(ln.replace('{{gap}}', 'x' * 9)) > 40:
        problems.append(f'{cid}/{v["id"]}: code line over 40 characters, too wide for a phone: {ln[:45]}')
  if len(json.dumps(c)) > 200_000: problems.append(f'{cid}: document too large')

n_tracks = sum(1 + (1 if c['scenario'] else 0) for _, c in C)
n_var = sum(len(c['recall']['variants']) + len((c['scenario'] or {}).get('variants', [])) for _, c in C)
types = sorted({v['type'] for _, c in C for v in c['recall']['variants']})
print(f'{len(C)} concepts, {n_tracks} tracks, {n_var} variants; recall types: {", ".join(types)}')
print('domains:', {d: sum(1 for _, c in C if c['domain'] == d) for d in '1234567'})
print('scenario share:', sum(1 for _, c in C if c['scenario']), 'of', len(C), '| pick-two variants:', sum(1 for _, c in C for v in (c['scenario'] or {}).get('variants', []) if v['pick'] == 2),
      '| flip pairs:', sum(1 for _, c in C for v in (c['scenario'] or {}).get('variants', []) if v.get('flip')) // 2)
for n in notes: print('note:', n)
if problems:
  print('PROBLEMS:'); [print(' -', p) for p in problems]; sys.exit(1)

json.dump(exam, open(f'{OUT}/exam.json', 'w'), ensure_ascii=False, indent=1)
for cid, c in C:
  if c['scenario'] is None: c = {k: v for k, v in c.items() if k != 'scenario'}
  json.dump(c, open(f'{OUT}/{cid}.json', 'w'), ensure_ascii=False, indent=1)
json.dump({'exams/databricks-dea': exam, **{f'concepts/{cid}': c for cid, c in C}}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'all.json'), 'w'), ensure_ascii=False)
print('written to', OUT)
