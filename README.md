# Analysing-The-Quality-Of-User-Stories-In-Open-Source-Projects

<h3>Data</h3>
All of the data is located in the data folder as follows:
<ul>
  <li>Initial datasets: /data/datasets</li>
  <li>Cleaned stories (AQUSA input): /data/cleaned_input_data
    <ul>
      <li>Files with ending _DS consist Descriptions and Summaries sepparately. Description has identifier 0 and Summary has identifier 1</li>
      <li>Files with ending _ALL consist concatenated Summaries and Descriptions (summary + ' ' + description) </li>
    </ul></li>
  <li>Defects (AQUSA output): /data/analyzed_output_data</li>
  <li>Quality scores for user stories: /data/quality_scores_data</li>
</ul> 

<h3>Data cleaning</h3>
<ul>
  <li>Cleaning for Summary and Description sepparately: /data_cleaning/cleaning_projects_DS.py</li>
  <li>Cleaning file where Summary and Description are concatenated (summary + ' ' + description): /data_cleaning/cleaning_projects_ALL.py</li>
</ul> 

<h3>Reading AQUSA outplut and plotting quality</h3>
<ul>
  <li>Analysing stories in Description field: /user_story_analysis/analysing_stories_description.py</li>
  <li>Analysing stories in Summary field: /user_story_analysis/analysing_stories_summary.py</li>
  <li>Choosing only best score story from Description or Summary: /user_story_analysis/analysing_stories_choose_better_score.py</li>
  <li>Analysing concatenated Summary and Desctiption: /user_story_analysis/analysing_stories_all.py</li>
</ul> 

<h3>User story quality forecasting (SARIMA) & measuring accuracy</h3>
<ul>
  <li>Located here: /user_story_analysis/analysing_stories_choose_better_score.py</li>
</ul> 

<h3>Descriptive analysis</h3>
<ul>
  <li>Plotting quality distribution COUNT (y axis - nr of stories; x axis - quality score): /descriptive_analysis/quality_distribution_count.py</li>
  <li>Plotting quality distribution PERCENTAGE (y axis - percentage of stories; x - axis quality score): /descriptive_analysis/quality_distribution_percentage.py</li>
  <li>Calculates nr of stories before cleaning, after cleaning and nr of bugs for all projects: /descriptive_analysis/descriptive_analysis_stories_bugs.py</li>
</ul> 

<h3>Bugs</h3>
<ul>
  <li>Plotting nr of bugs for all projects: /bugs_analysis/analysing_bugs.py/</li>
  <li>Correlation analysis (WTLCC): /cross_correlation_analysis/WTLCC_bugs.py/</li>
</ul> 

<h3>Rework</h3>
<ul>
  <li>Plotting rework: /rework_analysis/analysing_rework.py/</li>
  <li>Correlation analysis (WTLCC): /cross_correlation_analysis/WTLCC_rework.py/</li>
</ul> 

<h3>Delays</h3>
<ul>
  <li>Plotting delays: /bugs_analysis/analysing_delays.py/</li>
  <li>Correlation analysis (WTLCC): /cross_correlation_analysis/WTLCC_delays.py/</li>
</ul> 

<h3>Duration</h3>
<ul>
  <li>Plotting duration: /duration_analysis/analysing_duration.py/</li>
</ul> 

<h3>Duplicate requirements</h3>
<ul>
  <li>Plotting duplicate requirements: /duplicate_requirements_analysis/analysing_duplicates.py/</li>
</ul> 


