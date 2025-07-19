---
name: Improvement
about: Suggest an improvement to existing PyM Core functionality
title: '[IMPROVEMENT] '
labels: 'type/improvement, priority/medium'
assignees: ''

---

## 🔧 Improvement Description
A clear and concise description of what you'd like to improve in PyM Core.

## 📍 Current Situation
Describe how the current functionality works and what aspects could be better.

### Current Code/Behavior
```python
# Example of current implementation or usage
from pymcore import GenericElement

# Current way of doing things
element = GenericElement("id", "type")
element.set_parameter("height", 5000.0)  # Current API
```

## ✨ Proposed Improvement
Describe your suggested improvement.

### Improved Code/Behavior
```python
# Example of proposed improvement
from pymcore import GenericElement

# Improved way
element = GenericElement("id", "type")
element.height = 5000.0  # More intuitive API
# or
element.set_height(5.0, Unit.METER)  # Better validation
```

## 🎯 Benefits
Explain the benefits this improvement would provide:
- **Performance**: Does it make things faster?
- **Usability**: Does it make the API easier to use?
- **Maintainability**: Does it make the code easier to maintain?
- **Reliability**: Does it reduce errors or improve stability?

## 🔄 Backward Compatibility
- [ ] This change is backward compatible
- [ ] This change requires deprecation of existing functionality
- [ ] This change would break existing code (requires major version)

If breaking changes are needed, describe the migration path.

## 📊 Impact Assessment
- **Components Affected**: List which parts of PyM Core would be impacted
- **User Impact**: How would this affect existing users?
- **Implementation Complexity**: [Simple/Medium/Complex]

## 🏗️ Implementation Approach
If you have ideas about implementation:
- Technical approach
- Files that would need changes
- Tests that would need updates
- Documentation updates required

## 📋 Acceptance Criteria
- [ ] Improvement implemented as described
- [ ] Existing functionality preserved (if backward compatible)
- [ ] Tests updated/added for new behavior
- [ ] Documentation updated
- [ ] Performance impact measured (if applicable)

## 🔗 Related Issues
Link to any related issues or discussions.

## ⏱️ Estimated Effort
Rough estimate of implementation time:
- [ ] Small (< 1 day)
- [ ] Medium (1-3 days)  
- [ ] Large (> 3 days)

## ✅ Checklist
- [ ] I have clearly described the current situation and proposed improvement
- [ ] I have explained the benefits this improvement would provide
- [ ] I have considered backward compatibility implications
- [ ] I have searched existing issues to ensure this is not a duplicate