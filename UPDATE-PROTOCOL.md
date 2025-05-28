# Activation Manager - Update Protocol

## Standard Update Process

Follow this protocol for all code changes and feature implementations:

### 1. 📋 Planning Phase
- [ ] Create TodoWrite list for planned changes
- [ ] Mark current task as "in_progress"
- [ ] Identify affected components and files

### 2. 🔍 Investigation Phase
- [ ] Read relevant files to understand current implementation
- [ ] Analyze screenshots or bug reports if provided
- [ ] Identify root cause and solution approach

### 3. 💻 Implementation Phase
- [ ] Make code changes using Edit or MultiEdit tools
- [ ] Update TypeScript interfaces if needed
- [ ] Maintain existing code style and conventions
- [ ] Fix any TypeScript warnings or errors

### 4. 🧪 Testing Phase
- [ ] Build application: `npm run build`
- [ ] Verify successful compilation with no errors
- [ ] **Restart development server: `npm start`**
- [ ] Test functionality in browser at http://localhost:3000
- [ ] Mark testing todo as "completed"

### 5. 📚 Documentation Phase
- [ ] Update RELEASE-NOTES.md with changes
- [ ] Create or update relevant user stories if significant features
- [ ] Update product documentation if architectural changes
- [ ] Mark documentation todo as "completed"

### 6. 🚀 Deployment Phase
- [ ] Verify production build is ready
- [ ] Ensure all deployment files are current
- [ ] Mark deployment todo as "completed"
- [ ] Update TodoWrite to mark all tasks as "completed"

## Critical Requirements

### Always Include
- **Server Restart**: After any code changes, always restart the development server
- **Build Verification**: Every change must successfully build before completion
- **Documentation Updates**: All changes must be documented in release notes
- **Todo Tracking**: Use TodoWrite throughout the entire process

### Never Skip
- Production build testing (`npm run build`)
- Development server restart (`npm start`)
- Release notes updates
- Todo status management

### Error Handling
- If build fails, fix all TypeScript errors before proceeding
- If server fails to start, investigate and resolve before marking complete
- Always verify changes work in browser before completing

## Example Update Flow

```bash
# 1. Make code changes
# 2. Test build
npm run build

# 3. Restart server (REQUIRED)
npm start

# 4. Verify in browser
# Open http://localhost:3000

# 5. Update documentation
# Edit RELEASE-NOTES.md

# 6. Mark todos complete
```

## Quality Standards

- ✅ Zero TypeScript compilation errors
- ✅ Successful production build
- ✅ Development server running without issues
- ✅ All features tested in browser
- ✅ Documentation updated
- ✅ Todo list completed

This protocol ensures consistent, reliable updates while maintaining code quality and proper documentation.