This is where all the transformed and temporary data files reside.

TODO: The filetypes could possibly be changed when it is working (potentially speed things up).

Perhaps could store these files on S3 instead?

So far we have:
- `walk_info_df.xlsx` (form input into the labelling of workouts app) - MANUAL relocation - need to fix up path in notebook
- `walk_groups.xlsx` - list of the names of walks that each workout can be grouped into
- 