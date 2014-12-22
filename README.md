# TOGGLR

Very tiny Flask app that fetches data from Toggl's API and feeds it into
Geckoboard widgets.

Work in progress. Don't judge.


## To run

1. Install requirements.

2. Environment variables required:

    - `TOGGLR_TOGGL_API_TOKEN` - from toggl.com site under Profile.

    - `TOGGLR_TOGGL_WSID` - workspace_id from workspace settings URL on toggl.com
       site.

    - Alternatively, `TOGGLR_SETTINGS` can point to a Python file that sets the
      above variables (along with any other Flask config variables).

3. Run `python src/togglr.py`.


## Tests

Run `python tests.py`.
