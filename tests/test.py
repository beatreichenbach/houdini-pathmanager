import os

path = 'C:/parent1/parent2/parent3/file'
root = 'C:/parent1/parent2/parent3/parent4/parent5'

relative = os.path.relpath(path, root)
combined = os.path.join('$HIP', relative)

print(combined)

parts = combined.replace('\\', '/').split('/')
count = parts.count('..')
print(count)
