SELECT s.id, s.title, s.role, s.means, s.ends, d.highlight, d.kind, d.subkind, d.severity, d.false_positive
FROM stories as s
FULL OUTER JOIN defects as d
ON s.id = d.story_id
WHERE s.project_id = 16
and d.project_id = 16;