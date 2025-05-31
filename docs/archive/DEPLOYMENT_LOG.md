# Deployment Log

Track all deployments and any deviations from standard process.

## Format
```
Date: YYYY-MM-DD HH:MM
Version: stg-TIMESTAMP or prod-TIMESTAMP  
Deployer: Name
Type: [Feature|Fix|Hotfix|Emergency]
Staged: [Yes|No]
Notes: Description
```

---

## 2024 Deployments

### May 2024

**Date:** 2024-05-29 00:00  
**Version:** ui-cleanup-hotfix-20250529-081140  
**Deployer:** System  
**Type:** Hotfix  
**Staged:** No  
**Notes:** UI cleanup - removed visible password, changed to "NL Multi-Variate"

**Date:** 2024-05-29 00:00  
**Version:** stateless-fix-20250529-001049  
**Deployer:** System  
**Type:** Fix  
**Staged:** No  
**Notes:** Made all endpoints stateless for multi-instance support

**Date:** 2024-05-28 23:57  
**Version:** variable-picker-fix-20250528-235733  
**Deployer:** System  
**Type:** Fix  
**Staged:** No  
**Notes:** Fixed variable picker search and data loading

---

## Template for New Entries

```
**Date:** YYYY-MM-DD HH:MM  
**Version:** VERSION_NAME  
**Deployer:** Your Name  
**Type:** [Feature|Fix|Hotfix|Emergency]  
**Staged:** [Yes|No]  
**Notes:** What changed and why
```

## Emergency Deployment Justification

If staging was skipped, document why:
- Security vulnerability
- Production down
- Data corruption risk
- Customer impact severity

---

Note: Going forward, all deployments should go through staging first.