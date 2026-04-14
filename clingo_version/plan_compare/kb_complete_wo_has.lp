%%%%% for unsupported requirements, we put 'unsupported' and assume they are satisfied.
unsupported_prereq.     %%% assume unsupported prereqs are satisfied
unsupported_coreq.      %%% assume unsupported coreqs are satisfied
unsupported_pre_or_coreq. %%% assume unsupported pre_or_coreqs are satisfied
unsupported_anti_req.   %%% assume unsupported anti-reqs are satisfied
credits("CSE 101", 4).
anti_req("CSE 101", Sem) :- offered("CSE 101", Sem), not passed_before("CSE 114", Sem).
anti_req("CSE 101", Sem) :- offered("CSE 101", Sem), not passed_before("CSE 160", Sem).
coreq("CSE 101", Sem) :- offered("CSE 101", Sem).
pre_or_coreq("CSE 101", Sem) :- offered("CSE 101", Sem).
prereq("CSE 101", Sem) :- offered("CSE 101", Sem), unsupported_prereq.
credits("CSE 102", 3).
anti_req("CSE 102", Sem) :- offered("CSE 102", Sem).
coreq("CSE 102", Sem) :- offered("CSE 102", Sem).
pre_or_coreq("CSE 102", Sem) :- offered("CSE 102", Sem).
prereq("CSE 102", Sem) :- offered("CSE 102", Sem).
credits("CSE 110", 3).
anti_req("CSE 110", Sem) :- offered("CSE 110", Sem).
coreq("CSE 110", Sem) :- offered("CSE 110", Sem).
pre_or_coreq("CSE 110", Sem) :- offered("CSE 110", Sem).
prereq("CSE 110", Sem) :- offered("CSE 110", Sem), unsupported_prereq.
credits("CSE 113", 4).
anti_req("CSE 113", Sem) :- offered("CSE 113", Sem).
coreq("CSE 113", Sem) :- offered("CSE 113", Sem).
pre_or_coreq("CSE 113", Sem) :- offered("CSE 113", Sem).
prereq("CSE 113", Sem) :- offered("CSE 113", Sem), taken_before("AMS 151", Sem).
prereq("CSE 113", Sem) :- offered("CSE 113", Sem), taken_before("MAT 125", Sem).
prereq("CSE 113", Sem) :- offered("CSE 113", Sem), taken_before("MAT 131", Sem).
credits("CSE 114", 4).
anti_req("CSE 114", Sem) :- offered("CSE 114", Sem).
coreq("CSE 114", Sem) :- offered("CSE 114", Sem).
pre_or_coreq("CSE 114", Sem) :- offered("CSE 114", Sem).
prereq("CSE 114", Sem) :- offered("CSE 114", Sem), unsupported_prereq.
credits("CSE 130", 3).
anti_req("CSE 130", Sem) :- offered("CSE 130", Sem).
coreq("CSE 130", Sem) :- offered("CSE 130", Sem).
pre_or_coreq("CSE 130", Sem) :- offered("CSE 130", Sem).
prereq("CSE 130", Sem) :- offered("CSE 130", Sem), unsupported_prereq.
credits("CSE 150", 4).
anti_req("CSE 150", Sem) :- offered("CSE 150", Sem).
coreq("CSE 150", Sem) :- offered("CSE 150", Sem).
pre_or_coreq("CSE 150", Sem) :- offered("CSE 150", Sem).
prereq("CSE 150", Sem) :- offered("CSE 150", Sem), unsupported_prereq,unsupported_prereq.
credits("CSE 160", 3).
anti_req("CSE 160", Sem) :- offered("CSE 160", Sem).
coreq("CSE 160", Sem) :- offered("CSE 160", Sem), taken_together("CSE 161", Sem).
pre_or_coreq("CSE 160", Sem) :- offered("CSE 160", Sem).
prereq("CSE 160", Sem) :- offered("CSE 160", Sem), unsupported_prereq.
credits("CSE 161", 1).
anti_req("CSE 161", Sem) :- offered("CSE 161", Sem).
coreq("CSE 161", Sem) :- offered("CSE 161", Sem), taken_together("CSE 160", Sem).
pre_or_coreq("CSE 161", Sem) :- offered("CSE 161", Sem).
prereq("CSE 161", Sem) :- offered("CSE 161", Sem).
credits("CSE 190", 3).
anti_req("CSE 190", Sem) :- offered("CSE 190", Sem).
coreq("CSE 190", Sem) :- offered("CSE 190", Sem).
pre_or_coreq("CSE 190", Sem) :- offered("CSE 190", Sem).
prereq("CSE 190", Sem) :- offered("CSE 190", Sem).
credits("CSE 191", 3).
anti_req("CSE 191", Sem) :- offered("CSE 191", Sem).
coreq("CSE 191", Sem) :- offered("CSE 191", Sem).
pre_or_coreq("CSE 191", Sem) :- offered("CSE 191", Sem).
prereq("CSE 191", Sem) :- offered("CSE 191", Sem).
credits("CSE 192", 3).
anti_req("CSE 192", Sem) :- offered("CSE 192", Sem).
coreq("CSE 192", Sem) :- offered("CSE 192", Sem).
pre_or_coreq("CSE 192", Sem) :- offered("CSE 192", Sem).
prereq("CSE 192", Sem) :- offered("CSE 192", Sem).
credits("CSE 214", 4).
anti_req("CSE 214", Sem) :- offered("CSE 214", Sem).
coreq("CSE 214", Sem) :- offered("CSE 214", Sem).
pre_or_coreq("CSE 214", Sem) :- offered("CSE 214", Sem).
prereq("CSE 214", Sem) :- offered("CSE 214", Sem), passed_before("CSE 114", Sem).
credits("CSE 215", 4).
anti_req("CSE 215", Sem) :- offered("CSE 215", Sem).
coreq("CSE 215", Sem) :- offered("CSE 215", Sem).
pre_or_coreq("CSE 215", Sem) :- offered("CSE 215", Sem).
prereq("CSE 215", Sem) :- offered("CSE 215", Sem), taken_before("AMS 151", Sem).
prereq("CSE 215", Sem) :- offered("CSE 215", Sem), taken_before("MAT 125", Sem).
prereq("CSE 215", Sem) :- offered("CSE 215", Sem), taken_before("MAT 131", Sem).
credits("CSE 216", 4).
anti_req("CSE 216", Sem) :- offered("CSE 216", Sem).
coreq("CSE 216", Sem) :- offered("CSE 216", Sem).
pre_or_coreq("CSE 216", Sem) :- offered("CSE 216", Sem).
prereq("CSE 216", Sem) :- offered("CSE 216", Sem), passed_before("CSE 214", Sem),major("CSE").
credits("CSE 220", 4).
anti_req("CSE 220", Sem) :- offered("CSE 220", Sem).
coreq("CSE 220", Sem) :- offered("CSE 220", Sem).
pre_or_coreq("CSE 220", Sem) :- offered("CSE 220", Sem).
prereq("CSE 220", Sem) :- offered("CSE 220", Sem), unsupported_prereq.
credits("CSE 230", 3).
anti_req("CSE 230", Sem) :- offered("CSE 230", Sem).
coreq("CSE 230", Sem) :- offered("CSE 230", Sem).
pre_or_coreq("CSE 230", Sem) :- offered("CSE 230", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("CSE 130", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("CSE 220", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("ESE 124", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("ESG 111", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("BME 120", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("MEC 102", Sem).
credits("CSE 260", 3).
anti_req("CSE 260", Sem) :- offered("CSE 260", Sem).
coreq("CSE 260", Sem) :- offered("CSE 260", Sem), taken_together("CSE 261", Sem).
pre_or_coreq("CSE 260", Sem) :- offered("CSE 260", Sem).
prereq("CSE 260", Sem) :- offered("CSE 260", Sem), taken_before("CSE 160", Sem).
credits("CSE 261", 1).
anti_req("CSE 261", Sem) :- offered("CSE 261", Sem).
coreq("CSE 261", Sem) :- offered("CSE 261", Sem), taken_together("CSE 260", Sem).
pre_or_coreq("CSE 261", Sem) :- offered("CSE 261", Sem).
prereq("CSE 261", Sem) :- offered("CSE 261", Sem).
credits("CSE 300", 3).
anti_req("CSE 300", Sem) :- offered("CSE 300", Sem).
coreq("CSE 300", Sem) :- offered("CSE 300", Sem).
pre_or_coreq("CSE 300", Sem) :- offered("CSE 300", Sem).
prereq("CSE 300", Sem) :- offered("CSE 300", Sem), taken_before("WRT 102", Sem),major("CSE"; "ISE"; "DAS"),standing("U3"; "U4").
credits("CSE 301", 3).
anti_req("CSE 301", Sem) :- offered("CSE 301", Sem).
coreq("CSE 301", Sem) :- offered("CSE 301", Sem).
pre_or_coreq("CSE 301", Sem) :- offered("CSE 301", Sem).
prereq("CSE 301", Sem) :- offered("CSE 301", Sem), standing("U2").
prereq("CSE 301", Sem) :- offered("CSE 301", Sem), standing("U3").
prereq("CSE 301", Sem) :- offered("CSE 301", Sem), standing("U4").
credits("CSE 303", 3).
anti_req("CSE 303", Sem) :- offered("CSE 303", Sem).
coreq("CSE 303", Sem) :- offered("CSE 303", Sem).
pre_or_coreq("CSE 303", Sem) :- offered("CSE 303", Sem).
prereq("CSE 303", Sem) :- offered("CSE 303", Sem), passed_before(("CSE 160"; "CSE 214"), Sem),passed_before(("CSE 150"; "CSE 215"), Sem),major("CSE").
credits("CSE 304", 3).
anti_req("CSE 304", Sem) :- offered("CSE 304", Sem).
coreq("CSE 304", Sem) :- offered("CSE 304", Sem).
pre_or_coreq("CSE 304", Sem) :- offered("CSE 304", Sem).
prereq("CSE 304", Sem) :- offered("CSE 304", Sem), passed_before(("CSE 216"; "CSE 260"), Sem),passed_before("CSE 220", Sem).
credits("CSE 305", 3).
anti_req("CSE 305", Sem) :- offered("CSE 305", Sem).
coreq("CSE 305", Sem) :- offered("CSE 305", Sem).
pre_or_coreq("CSE 305", Sem) :- offered("CSE 305", Sem).
prereq("CSE 305", Sem) :- offered("CSE 305", Sem), passed_before("CSE 214", Sem),passed_before(("CSE 216"; "CSE 260"), Sem),major("CSE"; "DAS").
credits("CSE 306", 3).
anti_req("CSE 306", Sem) :- offered("CSE 306", Sem).
coreq("CSE 306", Sem) :- offered("CSE 306", Sem).
pre_or_coreq("CSE 306", Sem) :- offered("CSE 306", Sem).
prereq("CSE 306", Sem) :- offered("CSE 306", Sem), passed_before(("CSE 320"; "ESE 280"), Sem),major("CSE"; "ECE").
credits("CSE 307", 3).
anti_req("CSE 307", Sem) :- offered("CSE 307", Sem).
coreq("CSE 307", Sem) :- offered("CSE 307", Sem).
pre_or_coreq("CSE 307", Sem) :- offered("CSE 307", Sem).
prereq("CSE 307", Sem) :- offered("CSE 307", Sem), passed_before("CSE 214", Sem),passed_before(("CSE 216"; "CSE 260"), Sem),major("CSE"; "DAS").
credits("CSE 310", 3).
anti_req("CSE 310", Sem) :- offered("CSE 310", Sem).
coreq("CSE 310", Sem) :- offered("CSE 310", Sem).
pre_or_coreq("CSE 310", Sem) :- offered("CSE 310", Sem).
prereq("CSE 310", Sem) :- offered("CSE 310", Sem), passed_before(("CSE 214"; "CSE 260"), Sem),passed_before(("CSE 220"; "ISE 218"), Sem),major("CSE"; "ISE").
credits("CSE 311", 3).
anti_req("CSE 311", Sem) :- offered("CSE 311", Sem).
coreq("CSE 311", Sem) :- offered("CSE 311", Sem).
pre_or_coreq("CSE 311", Sem) :- offered("CSE 311", Sem).
prereq("CSE 311", Sem) :- offered("CSE 311", Sem), taken_before(("CSE 214"; "CSE 230"; "CSE 260"; "ISE 208"), Sem),major("ISE"; "CSE").
credits("CSE 312", 3).
anti_req("CSE 312", Sem) :- offered("CSE 312", Sem).
coreq("CSE 312", Sem) :- offered("CSE 312", Sem).
pre_or_coreq("CSE 312", Sem) :- offered("CSE 312", Sem).
prereq("CSE 312", Sem) :- offered("CSE 312", Sem), major("CSE"; "ISE"; "DAS"),standing("U3"; "U4"),unsupported_prereq.
credits("CSE 316", 3).
anti_req("CSE 316", Sem) :- offered("CSE 316", Sem).
coreq("CSE 316", Sem) :- offered("CSE 316", Sem).
pre_or_coreq("CSE 316", Sem) :- offered("CSE 316", Sem).
prereq("CSE 316", Sem) :- offered("CSE 316", Sem), passed_before(("CSE 214"; "CSE 260"), Sem),passed_before(("CSE 216"; "CSE 307"), Sem),major("CSE").
credits("CSE 320", 3).
anti_req("CSE 320", Sem) :- offered("CSE 320", Sem).
coreq("CSE 320", Sem) :- offered("CSE 320", Sem).
pre_or_coreq("CSE 320", Sem) :- offered("CSE 320", Sem).
prereq("CSE 320", Sem) :- offered("CSE 320", Sem), passed_before("CSE 220", Sem),major("CSE").
credits("CSE 323", 3).
anti_req("CSE 323", Sem) :- offered("CSE 323", Sem).
coreq("CSE 323", Sem) :- offered("CSE 323", Sem).
pre_or_coreq("CSE 323", Sem) :- offered("CSE 323", Sem).
prereq("CSE 323", Sem) :- offered("CSE 323", Sem), taken_before("CSE 214", Sem).
prereq("CSE 323", Sem) :- offered("CSE 323", Sem), taken_before("CSE 230", Sem).
prereq("CSE 323", Sem) :- offered("CSE 323", Sem), taken_before("CSE 260", Sem).
prereq("CSE 323", Sem) :- offered("CSE 323", Sem), taken_before("ISE 208", Sem).
credits("CSE 325", 3).
anti_req("CSE 325", Sem) :- offered("CSE 325", Sem).
coreq("CSE 325", Sem) :- offered("CSE 325", Sem).
pre_or_coreq("CSE 325", Sem) :- offered("CSE 325", Sem).
prereq("CSE 325", Sem) :- offered("CSE 325", Sem), taken_before("CSE 110", Sem).
prereq("CSE 325", Sem) :- offered("CSE 325", Sem), taken_before("CSE 101", Sem).
prereq("CSE 325", Sem) :- offered("CSE 325", Sem), taken_before("CSE 114", Sem).
credits("CSE 327", 3).
anti_req("CSE 327", Sem) :- offered("CSE 327", Sem).
coreq("CSE 327", Sem) :- offered("CSE 327", Sem).
pre_or_coreq("CSE 327", Sem) :- offered("CSE 327", Sem).
prereq("CSE 327", Sem) :- offered("CSE 327", Sem), taken_before(("CSE 214"; "CSE 230"; "CSE 260"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem),major("CSE"; "ISE"; "DAS").
credits("CSE 328", 3).
anti_req("CSE 328", Sem) :- offered("CSE 328", Sem).
coreq("CSE 328", Sem) :- offered("CSE 328", Sem).
pre_or_coreq("CSE 328", Sem) :- offered("CSE 328", Sem).
prereq("CSE 328", Sem) :- offered("CSE 328", Sem), passed_before("CSE 220", Sem),major("CSE"; "DAS").
credits("CSE 331", 3).
anti_req("CSE 331", Sem) :- offered("CSE 331", Sem).
coreq("CSE 331", Sem) :- offered("CSE 331", Sem).
pre_or_coreq("CSE 331", Sem) :- offered("CSE 331", Sem).
prereq("CSE 331", Sem) :- offered("CSE 331", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 332", 3).
anti_req("CSE 332", Sem) :- offered("CSE 332", Sem).
coreq("CSE 332", Sem) :- offered("CSE 332", Sem).
pre_or_coreq("CSE 332", Sem) :- offered("CSE 332", Sem).
prereq("CSE 332", Sem) :- offered("CSE 332", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),taken_before(("MAT 211"; "AMS 210"), Sem),taken_before(("AMS 110"; "AMS 310"), Sem),major("CSE"; "ISE"; "DAS").
credits("CSE 333", 3).
anti_req("CSE 333", Sem) :- offered("CSE 333", Sem).
coreq("CSE 333", Sem) :- offered("CSE 333", Sem).
pre_or_coreq("CSE 333", Sem) :- offered("CSE 333", Sem).
prereq("CSE 333", Sem) :- offered("CSE 333", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 334", 3).
anti_req("CSE 334", Sem) :- offered("CSE 334", Sem).
coreq("CSE 334", Sem) :- offered("CSE 334", Sem).
pre_or_coreq("CSE 334", Sem) :- offered("CSE 334", Sem).
prereq("CSE 334", Sem) :- offered("CSE 334", Sem), standing("U2"; "U3"; "U4"),major("CSE"; "ISE").
credits("CSE 336", 3).
anti_req("CSE 336", Sem) :- offered("CSE 336", Sem).
coreq("CSE 336", Sem) :- offered("CSE 336", Sem).
pre_or_coreq("CSE 336", Sem) :- offered("CSE 336", Sem).
prereq("CSE 336", Sem) :- offered("CSE 336", Sem), passed_before(("CSE 214"; "CSE 260"), Sem),major("CSE").
credits("CSE 337", 3).
anti_req("CSE 337", Sem) :- offered("CSE 337", Sem).
coreq("CSE 337", Sem) :- offered("CSE 337", Sem).
pre_or_coreq("CSE 337", Sem) :- offered("CSE 337", Sem).
prereq("CSE 337", Sem) :- offered("CSE 337", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE"; "DAS"),standing("U3"; "U4").
credits("CSE 350", 4).
anti_req("CSE 350", Sem) :- offered("CSE 350", Sem).
coreq("CSE 350", Sem) :- offered("CSE 350", Sem).
pre_or_coreq("CSE 350", Sem) :- offered("CSE 350", Sem).
prereq("CSE 350", Sem) :- offered("CSE 350", Sem), taken_before(("CSE 113"; "CSE 150"; "CSE 215"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem),unsupported_prereq.
credits("CSE 351", 3).
anti_req("CSE 351", Sem) :- offered("CSE 351", Sem).
coreq("CSE 351", Sem) :- offered("CSE 351", Sem).
pre_or_coreq("CSE 351", Sem) :- offered("CSE 351", Sem).
prereq("CSE 351", Sem) :- offered("CSE 351", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),taken_before("AMS 310", Sem),major("CSE"; "DAS").
credits("CSE 352", 3).
anti_req("CSE 352", Sem) :- offered("CSE 352", Sem).
coreq("CSE 352", Sem) :- offered("CSE 352", Sem).
pre_or_coreq("CSE 352", Sem) :- offered("CSE 352", Sem).
prereq("CSE 352", Sem) :- offered("CSE 352", Sem), taken_before(("CSE 316"; "CSE 351"), Sem),major("CSE"; "DAS").
credits("CSE 353", 3).
anti_req("CSE 353", Sem) :- offered("CSE 353", Sem).
coreq("CSE 353", Sem) :- offered("CSE 353", Sem).
pre_or_coreq("CSE 353", Sem) :- offered("CSE 353", Sem), taken_before_or_together("AMS 310", Sem).
pre_or_coreq("CSE 353", Sem) :- offered("CSE 353", Sem), taken_before_or_together("AMS 311", Sem).
pre_or_coreq("CSE 353", Sem) :- offered("CSE 353", Sem), taken_before_or_together("AMS 412", Sem).
prereq("CSE 353", Sem) :- offered("CSE 353", Sem), taken_before(("CSE 316"; "CSE 351"), Sem),major("CSE"; "DAS").
credits("CSE 354", 3).
anti_req("CSE 354", Sem) :- offered("CSE 354", Sem).
coreq("CSE 354", Sem) :- offered("CSE 354", Sem).
pre_or_coreq("CSE 354", Sem) :- offered("CSE 354", Sem).
prereq("CSE 354", Sem) :- offered("CSE 354", Sem), taken_before(("CSE 316"; "CSE 351"), Sem),major("CSE"; "DAS").
credits("CSE 355", 3).
anti_req("CSE 355", Sem) :- offered("CSE 355", Sem).
coreq("CSE 355", Sem) :- offered("CSE 355", Sem).
pre_or_coreq("CSE 355", Sem) :- offered("CSE 355", Sem).
prereq("CSE 355", Sem) :- offered("CSE 355", Sem), taken_before("AMS 301", Sem),unsupported_prereq.
credits("CSE 356", 3).
anti_req("CSE 356", Sem) :- offered("CSE 356", Sem).
coreq("CSE 356", Sem) :- offered("CSE 356", Sem).
pre_or_coreq("CSE 356", Sem) :- offered("CSE 356", Sem).
prereq("CSE 356", Sem) :- offered("CSE 356", Sem), passed_before("CSE 316", Sem),passed_before("CSE 320", Sem),major("CSE").
credits("CSE 357", 3).
anti_req("CSE 357", Sem) :- offered("CSE 357", Sem).
coreq("CSE 357", Sem) :- offered("CSE 357", Sem).
pre_or_coreq("CSE 357", Sem) :- offered("CSE 357", Sem).
prereq("CSE 357", Sem) :- offered("CSE 357", Sem), passed_before(("CSE 316"; "CSE 351"), Sem),passed_before("AMS 310", Sem),major("CSE"; "DAS").
credits("CSE 360", 3).
anti_req("CSE 360", Sem) :- offered("CSE 360", Sem).
coreq("CSE 360", Sem) :- offered("CSE 360", Sem).
pre_or_coreq("CSE 360", Sem) :- offered("CSE 360", Sem).
prereq("CSE 360", Sem) :- offered("CSE 360", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 361", 3).
anti_req("CSE 361", Sem) :- offered("CSE 361", Sem).
coreq("CSE 361", Sem) :- offered("CSE 361", Sem).
pre_or_coreq("CSE 361", Sem) :- offered("CSE 361", Sem).
prereq("CSE 361", Sem) :- offered("CSE 361", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 362", 3).
anti_req("CSE 362", Sem) :- offered("CSE 362", Sem).
coreq("CSE 362", Sem) :- offered("CSE 362", Sem).
pre_or_coreq("CSE 362", Sem) :- offered("CSE 362", Sem).
prereq("CSE 362", Sem) :- offered("CSE 362", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 363", 3).
anti_req("CSE 363", Sem) :- offered("CSE 363", Sem).
coreq("CSE 363", Sem) :- offered("CSE 363", Sem).
pre_or_coreq("CSE 363", Sem) :- offered("CSE 363", Sem).
prereq("CSE 363", Sem) :- offered("CSE 363", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 364", 3).
anti_req("CSE 364", Sem) :- offered("CSE 364", Sem).
coreq("CSE 364", Sem) :- offered("CSE 364", Sem).
pre_or_coreq("CSE 364", Sem) :- offered("CSE 364", Sem).
prereq("CSE 364", Sem) :- offered("CSE 364", Sem), taken_before("CSE 334", Sem).
prereq("CSE 364", Sem) :- offered("CSE 364", Sem), taken_before("ISE 334", Sem).
credits("CSE 366", 3).
anti_req("CSE 366", Sem) :- offered("CSE 366", Sem).
coreq("CSE 366", Sem) :- offered("CSE 366", Sem).
pre_or_coreq("CSE 366", Sem) :- offered("CSE 366", Sem).
prereq("CSE 366", Sem) :- offered("CSE 366", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),taken_before(("MAT 211"; "AMS 210"), Sem),major("CSE"; "ISE").
credits("CSE 370", 3).
anti_req("CSE 370", Sem) :- offered("CSE 370", Sem).
coreq("CSE 370", Sem) :- offered("CSE 370", Sem).
pre_or_coreq("CSE 370", Sem) :- offered("CSE 370", Sem).
prereq("CSE 370", Sem) :- offered("CSE 370", Sem), taken_before("CSE 310", Sem),major("CSE").
credits("CSE 371", 3).
anti_req("CSE 371", Sem) :- offered("CSE 371", Sem).
coreq("CSE 371", Sem) :- offered("CSE 371", Sem).
pre_or_coreq("CSE 371", Sem) :- offered("CSE 371", Sem).
prereq("CSE 371", Sem) :- offered("CSE 371", Sem), taken_before("CSE 113", Sem).
prereq("CSE 371", Sem) :- offered("CSE 371", Sem), taken_before("CSE 150", Sem).
prereq("CSE 371", Sem) :- offered("CSE 371", Sem), taken_before("CSE 215", Sem).
prereq("CSE 371", Sem) :- offered("CSE 371", Sem), taken_before("MAT 200", Sem).
prereq("CSE 371", Sem) :- offered("CSE 371", Sem), taken_before("MAT 250", Sem).
credits("CSE 373", 3).
anti_req("CSE 373", Sem) :- offered("CSE 373", Sem).
coreq("CSE 373", Sem) :- offered("CSE 373", Sem).
pre_or_coreq("CSE 373", Sem) :- offered("CSE 373", Sem).
prereq("CSE 373", Sem) :- offered("CSE 373", Sem), passed_before(("CSE 113"; "CSE 150"; "CSE 215"; "MAT 200"; "MAT 250"), Sem),passed_before(("MAT 211"; "AMS 210"), Sem),passed_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "MAT"; "DAS").
credits("CSE 376", 3).
anti_req("CSE 376", Sem) :- offered("CSE 376", Sem).
coreq("CSE 376", Sem) :- offered("CSE 376", Sem).
pre_or_coreq("CSE 376", Sem) :- offered("CSE 376", Sem).
prereq("CSE 376", Sem) :- offered("CSE 376", Sem), passed_before("CSE 320", Sem),major("CSE").
credits("CSE 377", 3).
anti_req("CSE 377", Sem) :- offered("CSE 377", Sem).
coreq("CSE 377", Sem) :- offered("CSE 377", Sem).
pre_or_coreq("CSE 377", Sem) :- offered("CSE 377", Sem).
prereq("CSE 377", Sem) :- offered("CSE 377", Sem), taken_before(("AMS 161"; "MAT 127"; "MAT 132"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem).
credits("CSE 378", 3).
anti_req("CSE 378", Sem) :- offered("CSE 378", Sem).
coreq("CSE 378", Sem) :- offered("CSE 378", Sem).
pre_or_coreq("CSE 378", Sem) :- offered("CSE 378", Sem).
prereq("CSE 378", Sem) :- offered("CSE 378", Sem), taken_before(("AMS 161"; "MAT 127"; "MAT 132"), Sem),taken_before(("AMS 210"; "MAT 211"; "MEC 262"), Sem).
credits("CSE 380", 3).
anti_req("CSE 380", Sem) :- offered("CSE 380", Sem).
coreq("CSE 380", Sem) :- offered("CSE 380", Sem).
pre_or_coreq("CSE 380", Sem) :- offered("CSE 380", Sem).
prereq("CSE 380", Sem) :- offered("CSE 380", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 381", 3).
anti_req("CSE 381", Sem) :- offered("CSE 381", Sem).
coreq("CSE 381", Sem) :- offered("CSE 381", Sem).
pre_or_coreq("CSE 381", Sem) :- offered("CSE 381", Sem).
prereq("CSE 381", Sem) :- offered("CSE 381", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 385", 4).
anti_req("CSE 385", Sem) :- offered("CSE 385", Sem).
coreq("CSE 385", Sem) :- offered("CSE 385", Sem).
pre_or_coreq("CSE 385", Sem) :- offered("CSE 385", Sem).
prereq("CSE 385", Sem) :- offered("CSE 385", Sem), taken_before(("CSE 113"; "CSE 150"; "CSE 215"; "MAT 200"; "MAT 250"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem),taken_before(("CSE 214"; "CSE 260"), Sem),unsupported_prereq.
credits("CSE 390", 3).
anti_req("CSE 390", Sem) :- offered("CSE 390", Sem).
coreq("CSE 390", Sem) :- offered("CSE 390", Sem).
pre_or_coreq("CSE 390", Sem) :- offered("CSE 390", Sem).
prereq("CSE 390", Sem) :- offered("CSE 390", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 391", 3).
anti_req("CSE 391", Sem) :- offered("CSE 391", Sem).
coreq("CSE 391", Sem) :- offered("CSE 391", Sem).
pre_or_coreq("CSE 391", Sem) :- offered("CSE 391", Sem).
prereq("CSE 391", Sem) :- offered("CSE 391", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 392", 3).
anti_req("CSE 392", Sem) :- offered("CSE 392", Sem).
coreq("CSE 392", Sem) :- offered("CSE 392", Sem).
pre_or_coreq("CSE 392", Sem) :- offered("CSE 392", Sem).
prereq("CSE 392", Sem) :- offered("CSE 392", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 393", 3).
anti_req("CSE 393", Sem) :- offered("CSE 393", Sem).
coreq("CSE 393", Sem) :- offered("CSE 393", Sem).
pre_or_coreq("CSE 393", Sem) :- offered("CSE 393", Sem).
prereq("CSE 393", Sem) :- offered("CSE 393", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 394", 3).
anti_req("CSE 394", Sem) :- offered("CSE 394", Sem).
coreq("CSE 394", Sem) :- offered("CSE 394", Sem).
pre_or_coreq("CSE 394", Sem) :- offered("CSE 394", Sem).
prereq("CSE 394", Sem) :- offered("CSE 394", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 416", 3).
anti_req("CSE 416", Sem) :- offered("CSE 416", Sem).
coreq("CSE 416", Sem) :- offered("CSE 416", Sem).
pre_or_coreq("CSE 416", Sem) :- offered("CSE 416", Sem).
prereq("CSE 416", Sem) :- offered("CSE 416", Sem), passed_before("CSE 316", Sem),standing("U4"),major("CSE").
credits("CSE 475", 3).
anti_req("CSE 475", Sem) :- offered("CSE 475", Sem).
coreq("CSE 475", Sem) :- offered("CSE 475", Sem).
pre_or_coreq("CSE 475", Sem) :- offered("CSE 475", Sem).
prereq("CSE 475", Sem) :- offered("CSE 475", Sem), unsupported_prereq,unsupported_prereq,unsupported_prereq.
credits("CSE 487", 0).
credits("CSE 487", 1).
credits("CSE 487", 2).
credits("CSE 487", 3).
anti_req("CSE 487", Sem) :- offered("CSE 487", Sem).
coreq("CSE 487", Sem) :- offered("CSE 487", Sem).
pre_or_coreq("CSE 487", Sem) :- offered("CSE 487", Sem).
prereq("CSE 487", Sem) :- offered("CSE 487", Sem), permission.
credits("CSE 488", 3).
anti_req("CSE 488", Sem) :- offered("CSE 488", Sem).
coreq("CSE 488", Sem) :- offered("CSE 488", Sem).
pre_or_coreq("CSE 488", Sem) :- offered("CSE 488", Sem).
prereq("CSE 488", Sem) :- offered("CSE 488", Sem), major("CSE"),standing("U3"; "U4"),permission.
credits("CSE 495", 3).
anti_req("CSE 495", Sem) :- offered("CSE 495", Sem).
coreq("CSE 495", Sem) :- offered("CSE 495", Sem).
pre_or_coreq("CSE 495", Sem) :- offered("CSE 495", Sem).
prereq("CSE 495", Sem) :- offered("CSE 495", Sem), unsupported_prereq,permission.
credits("CSE 496", 3).
anti_req("CSE 496", Sem) :- offered("CSE 496", Sem).
coreq("CSE 496", Sem) :- offered("CSE 496", Sem).
pre_or_coreq("CSE 496", Sem) :- offered("CSE 496", Sem).
prereq("CSE 496", Sem) :- offered("CSE 496", Sem), taken_before("CSE 495", Sem),permission.
credits("AMS 151", 3).
anti_req("AMS 151", Sem) :- offered("AMS 151", Sem).
coreq("AMS 151", Sem) :- offered("AMS 151", Sem).
pre_or_coreq("AMS 151", Sem) :- offered("AMS 151", Sem).
prereq("AMS 151", Sem) :- offered("AMS 151", Sem), passed_before_grade("MAT 123", "B", Sem).
credits("AMS 161", 3).
anti_req("AMS 161", Sem) :- offered("AMS 161", Sem).
coreq("AMS 161", Sem) :- offered("AMS 161", Sem).
pre_or_coreq("AMS 161", Sem) :- offered("AMS 161", Sem).
prereq("AMS 161", Sem) :- offered("AMS 161", Sem), passed_before("AMS 151", Sem).
prereq("AMS 161", Sem) :- offered("AMS 161", Sem), passed_before("MAT 131", Sem).
credits("AMS 210", 3).
anti_req("AMS 210", Sem) :- offered("AMS 210", Sem).
coreq("AMS 210", Sem) :- offered("AMS 210", Sem).
pre_or_coreq("AMS 210", Sem) :- offered("AMS 210", Sem).
prereq("AMS 210", Sem) :- offered("AMS 210", Sem), taken_before("AMS 151", Sem).
prereq("AMS 210", Sem) :- offered("AMS 210", Sem), taken_before("MAT 131", Sem).
prereq("AMS 210", Sem) :- offered("AMS 210", Sem), taken_same("MAT 126").
credits("AMS 301", 3).
anti_req("AMS 301", Sem) :- offered("AMS 301", Sem).
coreq("AMS 301", Sem) :- offered("AMS 301", Sem).
pre_or_coreq("AMS 301", Sem) :- offered("AMS 301", Sem).
prereq("AMS 301", Sem) :- offered("AMS 301", Sem), taken_before("AMS 210", Sem).
prereq("AMS 301", Sem) :- offered("AMS 301", Sem), taken_before("MAT 211", Sem).
prereq("AMS 301", Sem) :- offered("AMS 301", Sem), taken_before("AMS 361", Sem).
prereq("AMS 301", Sem) :- offered("AMS 301", Sem), taken_before("MAT 303", Sem).
credits("AMS 310", 3).
anti_req("AMS 310", Sem) :- offered("AMS 310", Sem).
coreq("AMS 310", Sem) :- offered("AMS 310", Sem).
pre_or_coreq("AMS 310", Sem) :- offered("AMS 310", Sem).
prereq("AMS 310", Sem) :- offered("AMS 310", Sem), taken_before("AMS 161", Sem).
prereq("AMS 310", Sem) :- offered("AMS 310", Sem), taken_before("MAT 132", Sem).
prereq("AMS 310", Sem) :- offered("AMS 310", Sem), taken_before("MAT 127", Sem).
credits("AMS 311", 3).
anti_req("AMS 311", Sem) :- offered("AMS 311", Sem).
coreq("AMS 311", Sem) :- offered("AMS 311", Sem), taken_together("MAT 203", Sem).
coreq("AMS 311", Sem) :- offered("AMS 311", Sem), taken_together("AMS 261", Sem).
pre_or_coreq("AMS 311", Sem) :- offered("AMS 311", Sem).
prereq("AMS 311", Sem) :- offered("AMS 311", Sem), taken_before("AMS 301", Sem),taken_before("AMS 310", Sem).
prereq("AMS 311", Sem) :- offered("AMS 311", Sem), permission.
credits("MAT 123", 3).
anti_req("MAT 123", Sem) :- offered("MAT 123", Sem).
coreq("MAT 123", Sem) :- offered("MAT 123", Sem).
pre_or_coreq("MAT 123", Sem) :- offered("MAT 123", Sem).
prereq("MAT 123", Sem) :- offered("MAT 123", Sem), unsupported_prereq.
credits("MAT 125", 3).
anti_req("MAT 125", Sem) :- offered("MAT 125", Sem).
coreq("MAT 125", Sem) :- offered("MAT 125", Sem).
pre_or_coreq("MAT 125", Sem) :- offered("MAT 125", Sem).
prereq("MAT 125", Sem) :- offered("MAT 125", Sem), passed_before("MAT 123", Sem).
prereq("MAT 125", Sem) :- offered("MAT 125", Sem), taken_same("MAT 130").
credits("MAT 126", 3).
anti_req("MAT 126", Sem) :- offered("MAT 126", Sem).
coreq("MAT 126", Sem) :- offered("MAT 126", Sem).
pre_or_coreq("MAT 126", Sem) :- offered("MAT 126", Sem).
prereq("MAT 126", Sem) :- offered("MAT 126", Sem), passed_before("MAT 125", Sem).
prereq("MAT 126", Sem) :- offered("MAT 126", Sem), passed_before("MAT 131", Sem).
prereq("MAT 126", Sem) :- offered("MAT 126", Sem), passed_before("MAT 141", Sem).
prereq("MAT 126", Sem) :- offered("MAT 126", Sem), passed_before("AMS 151", Sem).
credits("MAT 127", 3).
anti_req("MAT 127", Sem) :- offered("MAT 127", Sem).
coreq("MAT 127", Sem) :- offered("MAT 127", Sem).
pre_or_coreq("MAT 127", Sem) :- offered("MAT 127", Sem).
prereq("MAT 127", Sem) :- offered("MAT 127", Sem), passed_before("MAT 126", Sem).
credits("MAT 131", 4).
anti_req("MAT 131", Sem) :- offered("MAT 131", Sem).
coreq("MAT 131", Sem) :- offered("MAT 131", Sem).
pre_or_coreq("MAT 131", Sem) :- offered("MAT 131", Sem).
prereq("MAT 131", Sem) :- offered("MAT 131", Sem), passed_before_grade("MAT 123", "B", Sem).
credits("MAT 132", 4).
anti_req("MAT 132", Sem) :- offered("MAT 132", Sem).
coreq("MAT 132", Sem) :- offered("MAT 132", Sem).
pre_or_coreq("MAT 132", Sem) :- offered("MAT 132", Sem).
prereq("MAT 132", Sem) :- offered("MAT 132", Sem), passed_before("AMS 151", Sem).
prereq("MAT 132", Sem) :- offered("MAT 132", Sem), passed_before("MAT 131", Sem).
prereq("MAT 132", Sem) :- offered("MAT 132", Sem), passed_before("MAT 141", Sem).
credits("MAT 211", 3).
anti_req("MAT 211", Sem) :- offered("MAT 211", Sem).
coreq("MAT 211", Sem) :- offered("MAT 211", Sem).
pre_or_coreq("MAT 211", Sem) :- offered("MAT 211", Sem).
prereq("MAT 211", Sem) :- offered("MAT 211", Sem), passed_before("AMS 151", Sem).
prereq("MAT 211", Sem) :- offered("MAT 211", Sem), passed_before("MAT 131", Sem).
prereq("MAT 211", Sem) :- offered("MAT 211", Sem), passed_before("MAT 141", Sem).
prereq("MAT 211", Sem) :- offered("MAT 211", Sem), taken_same("MAT 126").
credits("BIO 201", 3).
anti_req("BIO 201", Sem) :- offered("BIO 201", Sem).
coreq("BIO 201", Sem) :- offered("BIO 201", Sem).
pre_or_coreq("BIO 201", Sem) :- offered("BIO 201", Sem).
prereq("BIO 201", Sem) :- offered("BIO 201", Sem), unsupported_prereq.
credits("BIO 202", 3).
anti_req("BIO 202", Sem) :- offered("BIO 202", Sem).
coreq("BIO 202", Sem) :- offered("BIO 202", Sem).
pre_or_coreq("BIO 202", Sem) :- offered("BIO 202", Sem).
prereq("BIO 202", Sem) :- offered("BIO 202", Sem), passed_before("CHE 129", Sem).
prereq("BIO 202", Sem) :- offered("BIO 202", Sem), passed_before("CHE 131", Sem).
prereq("BIO 202", Sem) :- offered("BIO 202", Sem), taken_same("CHE 152").
credits("BIO 203", 3).
anti_req("BIO 203", Sem) :- offered("BIO 203", Sem).
coreq("BIO 203", Sem) :- offered("BIO 203", Sem).
pre_or_coreq("BIO 203", Sem) :- offered("BIO 203", Sem).
prereq("BIO 203", Sem) :- offered("BIO 203", Sem), taken_before("CHE 129", Sem).
prereq("BIO 203", Sem) :- offered("BIO 203", Sem), taken_before("CHE 131", Sem).
prereq("BIO 203", Sem) :- offered("BIO 203", Sem), taken_same("CHE 152").
credits("BIO 204", 2).
anti_req("BIO 204", Sem) :- offered("BIO 204", Sem).
coreq("BIO 204", Sem) :- offered("BIO 204", Sem).
pre_or_coreq("BIO 204", Sem) :- offered("BIO 204", Sem).
prereq("BIO 204", Sem) :- offered("BIO 204", Sem), taken_before("CHE 129", Sem),taken_before("CHE 131", Sem).
prereq("BIO 204", Sem) :- offered("BIO 204", Sem), taken_same("CHE 152").
credits("CHE 131", 4).
anti_req("CHE 131", Sem) :- offered("CHE 131", Sem).
coreq("CHE 131", Sem) :- offered("CHE 131", Sem), unsupported_coreq.
pre_or_coreq("CHE 131", Sem) :- offered("CHE 131", Sem).
prereq("CHE 131", Sem) :- offered("CHE 131", Sem), unsupported_prereq.
credits("CHE 132", 4).
anti_req("CHE 132", Sem) :- offered("CHE 132", Sem).
coreq("CHE 132", Sem) :- offered("CHE 132", Sem).
pre_or_coreq("CHE 132", Sem) :- offered("CHE 132", Sem), unsupported_pre_or_coreq,unsupported_pre_or_coreq.
prereq("CHE 132", Sem) :- offered("CHE 132", Sem), passed_before("CHE 129", Sem).
prereq("CHE 132", Sem) :- offered("CHE 132", Sem), passed_before("CHE 131", Sem).
credits("CHE 133", 1).
anti_req("CHE 133", Sem) :- offered("CHE 133", Sem).
coreq("CHE 133", Sem) :- offered("CHE 133", Sem).
pre_or_coreq("CHE 133", Sem) :- offered("CHE 133", Sem).
prereq("CHE 133", Sem) :- offered("CHE 133", Sem).
credits("CHE 152", 4).
anti_req("CHE 152", Sem) :- offered("CHE 152", Sem).
coreq("CHE 152", Sem) :- offered("CHE 152", Sem).
pre_or_coreq("CHE 152", Sem) :- offered("CHE 152", Sem).
prereq("CHE 152", Sem) :- offered("CHE 152", Sem), unsupported_prereq,unsupported_prereq.
credits("CHE 154", 2).
anti_req("CHE 154", Sem) :- offered("CHE 154", Sem).
coreq("CHE 154", Sem) :- offered("CHE 154", Sem), taken_together("CHE 152", Sem).
pre_or_coreq("CHE 154", Sem) :- offered("CHE 154", Sem).
prereq("CHE 154", Sem) :- offered("CHE 154", Sem).
credits("CHE 321", 4).
anti_req("CHE 321", Sem) :- offered("CHE 321", Sem).
coreq("CHE 321", Sem) :- offered("CHE 321", Sem).
pre_or_coreq("CHE 321", Sem) :- offered("CHE 321", Sem).
prereq("CHE 321", Sem) :- offered("CHE 321", Sem), passed_before("CHE 132", Sem).
credits("CHE 322", 4).
anti_req("CHE 322", Sem) :- offered("CHE 322", Sem).
coreq("CHE 322", Sem) :- offered("CHE 322", Sem).
pre_or_coreq("CHE 322", Sem) :- offered("CHE 322", Sem).
prereq("CHE 322", Sem) :- offered("CHE 322", Sem), passed_before("CHE 321", Sem).
credits("CHE 331", 4).
anti_req("CHE 331", Sem) :- offered("CHE 331", Sem).
coreq("CHE 331", Sem) :- offered("CHE 331", Sem), taken_together("CHE 383", Sem).
pre_or_coreq("CHE 331", Sem) :- offered("CHE 331", Sem).
prereq("CHE 331", Sem) :- offered("CHE 331", Sem), passed_before("CHE 152", Sem).
credits("CHE 332", 4).
anti_req("CHE 332", Sem) :- offered("CHE 332", Sem).
coreq("CHE 332", Sem) :- offered("CHE 332", Sem).
pre_or_coreq("CHE 332", Sem) :- offered("CHE 332", Sem).
prereq("CHE 332", Sem) :- offered("CHE 332", Sem), passed_before("CHE 331", Sem).
credits("PHY 125", 3).
anti_req("PHY 125", Sem) :- offered("PHY 125", Sem).
coreq("PHY 125", Sem) :- offered("PHY 125", Sem).
pre_or_coreq("PHY 125", Sem) :- offered("PHY 125", Sem).
prereq("PHY 125", Sem) :- offered("PHY 125", Sem), taken_before("MAT 125", Sem).
credits("PHY 126", 3).
anti_req("PHY 126", Sem) :- offered("PHY 126", Sem).
coreq("PHY 126", Sem) :- offered("PHY 126", Sem).
pre_or_coreq("PHY 126", Sem) :- offered("PHY 126", Sem).
prereq("PHY 126", Sem) :- offered("PHY 126", Sem), passed_before("PHY 125", Sem).
prereq("PHY 126", Sem) :- offered("PHY 126", Sem), passed_before("PHY 131", Sem).
prereq("PHY 126", Sem) :- offered("PHY 126", Sem), passed_before("PHY 141", Sem).
credits("PHY 127", 3).
anti_req("PHY 127", Sem) :- offered("PHY 127", Sem).
coreq("PHY 127", Sem) :- offered("PHY 127", Sem).
pre_or_coreq("PHY 127", Sem) :- offered("PHY 127", Sem).
prereq("PHY 127", Sem) :- offered("PHY 127", Sem), passed_before("PHY 125", Sem).
prereq("PHY 127", Sem) :- offered("PHY 127", Sem), passed_before("PHY 131", Sem).
prereq("PHY 127", Sem) :- offered("PHY 127", Sem), passed_before("PHY 141", Sem).
credits("PHY 131", 3).
anti_req("PHY 131", Sem) :- offered("PHY 131", Sem).
coreq("PHY 131", Sem) :- offered("PHY 131", Sem).
pre_or_coreq("PHY 131", Sem) :- offered("PHY 131", Sem).
prereq("PHY 131", Sem) :- offered("PHY 131", Sem), unsupported_prereq.
credits("PHY 132", 3).
anti_req("PHY 132", Sem) :- offered("PHY 132", Sem).
coreq("PHY 132", Sem) :- offered("PHY 132", Sem).
pre_or_coreq("PHY 132", Sem) :- offered("PHY 132", Sem).
prereq("PHY 132", Sem) :- offered("PHY 132", Sem), passed_before("PHY 131", Sem).
prereq("PHY 132", Sem) :- offered("PHY 132", Sem), passed_before("PHY 141", Sem).
credits("PHY 133", 1).
anti_req("PHY 133", Sem) :- offered("PHY 133", Sem).
coreq("PHY 133", Sem) :- offered("PHY 133", Sem).
pre_or_coreq("PHY 133", Sem) :- offered("PHY 133", Sem), taken_before_or_together("PHY 125", Sem),taken_before_or_together("PHY 126", Sem).
pre_or_coreq("PHY 133", Sem) :- offered("PHY 133", Sem), taken_before_or_together("PHY 131", Sem).
pre_or_coreq("PHY 133", Sem) :- offered("PHY 133", Sem), taken_before_or_together("PHY 141", Sem).
prereq("PHY 133", Sem) :- offered("PHY 133", Sem).
credits("PHY 134", 1).
anti_req("PHY 134", Sem) :- offered("PHY 134", Sem).
coreq("PHY 134", Sem) :- offered("PHY 134", Sem).
pre_or_coreq("PHY 134", Sem) :- offered("PHY 134", Sem).
prereq("PHY 134", Sem) :- offered("PHY 134", Sem), passed_before("PHY 133", Sem).
credits("PHY 141", 3).
anti_req("PHY 141", Sem) :- offered("PHY 141", Sem).
coreq("PHY 141", Sem) :- offered("PHY 141", Sem).
pre_or_coreq("PHY 141", Sem) :- offered("PHY 141", Sem).
prereq("PHY 141", Sem) :- offered("PHY 141", Sem).
credits("PHY 142", 3).
anti_req("PHY 142", Sem) :- offered("PHY 142", Sem).
coreq("PHY 142", Sem) :- offered("PHY 142", Sem).
pre_or_coreq("PHY 142", Sem) :- offered("PHY 142", Sem).
prereq("PHY 142", Sem) :- offered("PHY 142", Sem), passed_before("PHY 141", Sem).
prereq("PHY 142", Sem) :- offered("PHY 142", Sem), permission.
credits("PHY 251", 3).
anti_req("PHY 251", Sem) :- offered("PHY 251", Sem).
coreq("PHY 251", Sem) :- offered("PHY 251", Sem).
pre_or_coreq("PHY 251", Sem) :- offered("PHY 251", Sem), taken_before_or_together("MAT 203", Sem).
pre_or_coreq("PHY 251", Sem) :- offered("PHY 251", Sem), taken_before_or_together("MAT 205", Sem).
pre_or_coreq("PHY 251", Sem) :- offered("PHY 251", Sem), taken_before_or_together("AMS 261", Sem).
pre_or_coreq("PHY 251", Sem) :- offered("PHY 251", Sem), taken_before_or_together("MAT 307", Sem).
prereq("PHY 251", Sem) :- offered("PHY 251", Sem), aux_or_1(Sem),taken_before("PHY 134", Sem),passed_before(("MAT 126"; "MAT 132"; "MAT 142"; "MAT 171"; "AMS 161"), Sem).
credits("PHY 252", 1).
anti_req("PHY 252", Sem) :- offered("PHY 252", Sem).
coreq("PHY 252", Sem) :- offered("PHY 252", Sem).
pre_or_coreq("PHY 252", Sem) :- offered("PHY 252", Sem), taken_before_or_together("PHY 251", Sem).
prereq("PHY 252", Sem) :- offered("PHY 252", Sem).
credits("GEO 102", 3).
anti_req("GEO 102", Sem) :- offered("GEO 102", Sem).
coreq("GEO 102", Sem) :- offered("GEO 102", Sem).
pre_or_coreq("GEO 102", Sem) :- offered("GEO 102", Sem).
prereq("GEO 102", Sem) :- offered("GEO 102", Sem).
credits("GEO 103", 3).
anti_req("GEO 103", Sem) :- offered("GEO 103", Sem).
coreq("GEO 103", Sem) :- offered("GEO 103", Sem).
pre_or_coreq("GEO 103", Sem) :- offered("GEO 103", Sem).
prereq("GEO 103", Sem) :- offered("GEO 103", Sem).
credits("GEO 112", 1).
anti_req("GEO 112", Sem) :- offered("GEO 112", Sem).
coreq("GEO 112", Sem) :- offered("GEO 112", Sem).
pre_or_coreq("GEO 112", Sem) :- offered("GEO 112", Sem).
prereq("GEO 112", Sem) :- offered("GEO 112", Sem).
credits("GEO 122", 4).
anti_req("GEO 122", Sem) :- offered("GEO 122", Sem).
coreq("GEO 122", Sem) :- offered("GEO 122", Sem).
pre_or_coreq("GEO 122", Sem) :- offered("GEO 122", Sem).
prereq("GEO 122", Sem) :- offered("GEO 122", Sem).
credits("AST 203", 4).
anti_req("AST 203", Sem) :- offered("AST 203", Sem).
coreq("AST 203", Sem) :- offered("AST 203", Sem).
pre_or_coreq("AST 203", Sem) :- offered("AST 203", Sem).
prereq("AST 203", Sem) :- offered("AST 203", Sem), taken_before("PHY 125", Sem).
prereq("AST 203", Sem) :- offered("AST 203", Sem), taken_before("PHY 133", Sem).
prereq("AST 203", Sem) :- offered("AST 203", Sem), taken_before("PHY 131", Sem).
prereq("AST 203", Sem) :- offered("AST 203", Sem), taken_before("PHY 141", Sem).
credits("AST 205", 3).
anti_req("AST 205", Sem) :- offered("AST 205", Sem).
coreq("AST 205", Sem) :- offered("AST 205", Sem).
pre_or_coreq("AST 205", Sem) :- offered("AST 205", Sem).
prereq("AST 205", Sem) :- offered("AST 205", Sem), taken_before("PHY 125", Sem).
prereq("AST 205", Sem) :- offered("AST 205", Sem), taken_before("PHY 133", Sem).
prereq("AST 205", Sem) :- offered("AST 205", Sem), taken_before("PHY 131", Sem).
prereq("AST 205", Sem) :- offered("AST 205", Sem), taken_before("PHY 141", Sem).
credits("WRT 101", 3).
anti_req("WRT 101", Sem) :- offered("WRT 101", Sem).
coreq("WRT 101", Sem) :- offered("WRT 101", Sem).
pre_or_coreq("WRT 101", Sem) :- offered("WRT 101", Sem).
prereq("WRT 101", Sem) :- offered("WRT 101", Sem), unsupported_prereq.
credits("WRT 102", 3).
anti_req("WRT 102", Sem) :- offered("WRT 102", Sem).
coreq("WRT 102", Sem) :- offered("WRT 102", Sem).
pre_or_coreq("WRT 102", Sem) :- offered("WRT 102", Sem).
prereq("WRT 102", Sem) :- offered("WRT 102", Sem), passed_before("WRT 101", Sem).
credits("AMS 110", 3).
anti_req("AMS 110", Sem) :- offered("AMS 110", Sem), not passed_before("MAT 203", Sem).
anti_req("AMS 110", Sem) :- offered("AMS 110", Sem), not passed_before("AMS 310", Sem).
coreq("AMS 110", Sem) :- offered("AMS 110", Sem).
pre_or_coreq("AMS 110", Sem) :- offered("AMS 110", Sem).
prereq("AMS 110", Sem) :- offered("AMS 110", Sem), taken_before("AMS 151", Sem).
prereq("AMS 110", Sem) :- offered("AMS 110", Sem), taken_before("MAT 125", Sem).
prereq("AMS 110", Sem) :- offered("AMS 110", Sem), taken_before("MAT 131", Sem).
credits("AMS 261", 4).
anti_req("AMS 261", Sem) :- offered("AMS 261", Sem).
coreq("AMS 261", Sem) :- offered("AMS 261", Sem).
pre_or_coreq("AMS 261", Sem) :- offered("AMS 261", Sem).
prereq("AMS 261", Sem) :- offered("AMS 261", Sem), taken_before("AMS 161", Sem).
prereq("AMS 261", Sem) :- offered("AMS 261", Sem), taken_before("MAT 127", Sem).
prereq("AMS 261", Sem) :- offered("AMS 261", Sem), taken_before("MAT 132", Sem).
credits("AMS 361", 4).
anti_req("AMS 361", Sem) :- offered("AMS 361", Sem).
coreq("AMS 361", Sem) :- offered("AMS 361", Sem).
pre_or_coreq("AMS 361", Sem) :- offered("AMS 361", Sem).
prereq("AMS 361", Sem) :- offered("AMS 361", Sem), taken_before("AMS 161", Sem).
prereq("AMS 361", Sem) :- offered("AMS 361", Sem), taken_before("MAT 127", Sem).
prereq("AMS 361", Sem) :- offered("AMS 361", Sem), taken_before("MAT 132", Sem).
credits("AMS 412", 3).
anti_req("AMS 412", Sem) :- offered("AMS 412", Sem).
coreq("AMS 412", Sem) :- offered("AMS 412", Sem).
pre_or_coreq("AMS 412", Sem) :- offered("AMS 412", Sem).
prereq("AMS 412", Sem) :- offered("AMS 412", Sem), taken_before("AMS 311", Sem).
credits("MAT 130", 1).
anti_req("MAT 130", Sem) :- offered("MAT 130", Sem).
coreq("MAT 130", Sem) :- offered("MAT 130", Sem).
pre_or_coreq("MAT 130", Sem) :- offered("MAT 130", Sem).
prereq("MAT 130", Sem) :- offered("MAT 130", Sem), taken_before("MAT 122", Sem).
prereq("MAT 130", Sem) :- offered("MAT 130", Sem), permission.
credits("MAT 200", 3).
anti_req("MAT 200", Sem) :- offered("MAT 200", Sem).
coreq("MAT 200", Sem) :- offered("MAT 200", Sem).
pre_or_coreq("MAT 200", Sem) :- offered("MAT 200", Sem).
prereq("MAT 200", Sem) :- offered("MAT 200", Sem), unsupported_prereq.
credits("MAT 203", 4).
anti_req("MAT 203", Sem) :- offered("MAT 203", Sem).
coreq("MAT 203", Sem) :- offered("MAT 203", Sem).
pre_or_coreq("MAT 203", Sem) :- offered("MAT 203", Sem).
prereq("MAT 203", Sem) :- offered("MAT 203", Sem), passed_before("MAT 127", Sem).
prereq("MAT 203", Sem) :- offered("MAT 203", Sem), passed_before("MAT 132", Sem).
prereq("MAT 203", Sem) :- offered("MAT 203", Sem), passed_before("MAT 142", Sem).
prereq("MAT 203", Sem) :- offered("MAT 203", Sem), passed_before("AMS 161", Sem).
credits("MAT 250", 4).
anti_req("MAT 250", Sem) :- offered("MAT 250", Sem).
coreq("MAT 250", Sem) :- offered("MAT 250", Sem).
pre_or_coreq("MAT 250", Sem) :- offered("MAT 250", Sem).
prereq("MAT 250", Sem) :- offered("MAT 250", Sem), taken_before("MAT 131", Sem).
credits("MAT 303", 4).
anti_req("MAT 303", Sem) :- offered("MAT 303", Sem).
coreq("MAT 303", Sem) :- offered("MAT 303", Sem).
pre_or_coreq("MAT 303", Sem) :- offered("MAT 303", Sem).
prereq("MAT 303", Sem) :- offered("MAT 303", Sem), passed_before("MAT 127", Sem).
prereq("MAT 303", Sem) :- offered("MAT 303", Sem), passed_before("MAT 132", Sem).
prereq("MAT 303", Sem) :- offered("MAT 303", Sem), passed_before("MAT 142", Sem).
prereq("MAT 303", Sem) :- offered("MAT 303", Sem), passed_before("AMS 161", Sem).
credits("MAT 307", 4).
anti_req("MAT 307", Sem) :- offered("MAT 307", Sem).
coreq("MAT 307", Sem) :- offered("MAT 307", Sem).
pre_or_coreq("MAT 307", Sem) :- offered("MAT 307", Sem).
prereq("MAT 307", Sem) :- offered("MAT 307", Sem), taken_before("MAT 127", Sem).
prereq("MAT 307", Sem) :- offered("MAT 307", Sem), taken_before("MAT 132", Sem).
credits("CHE 129", 4).
anti_req("CHE 129", Sem) :- offered("CHE 129", Sem).
coreq("CHE 129", Sem) :- offered("CHE 129", Sem), taken_together("CHE 130", Sem),taken_together("MAT 123", Sem).
pre_or_coreq("CHE 129", Sem) :- offered("CHE 129", Sem).
prereq("CHE 129", Sem) :- offered("CHE 129", Sem), unsupported_prereq.
credits("CHE 383", 2).
anti_req("CHE 383", Sem) :- offered("CHE 383", Sem).
coreq("CHE 383", Sem) :- offered("CHE 383", Sem), taken_together("CHE 331", Sem).
pre_or_coreq("CHE 383", Sem) :- offered("CHE 383", Sem).
prereq("CHE 383", Sem) :- offered("CHE 383", Sem), taken_before("CHE 154", Sem).
credits("PHY 122", 4).
anti_req("PHY 122", Sem) :- offered("PHY 122", Sem).
coreq("PHY 122", Sem) :- offered("PHY 122", Sem).
pre_or_coreq("PHY 122", Sem) :- offered("PHY 122", Sem), taken_before_or_together("CHE 132", Sem).
pre_or_coreq("PHY 122", Sem) :- offered("PHY 122", Sem), taken_before_or_together("CHE 152", Sem).
prereq("PHY 122", Sem) :- offered("PHY 122", Sem), passed_before("PHY 121", Sem).
credits("CHE 130", 1).
anti_req("CHE 130", Sem) :- offered("CHE 130", Sem).
coreq("CHE 130", Sem) :- offered("CHE 130", Sem), taken_together("CHE 129", Sem),taken_together("MAT 123", Sem).
pre_or_coreq("CHE 130", Sem) :- offered("CHE 130", Sem).
prereq("CHE 130", Sem) :- offered("CHE 130", Sem).
aux_or_1(Sem) :- taken_before("PHY 122", Sem),taken_before("PHY 124", Sem).
aux_or_1(Sem) :- taken_before("PHY 126", Sem),taken_before("PHY 127", Sem).
aux_or_1(Sem) :- taken_before("PHY 132", Sem).
aux_or_1(Sem) :- taken_before("PHY 142", Sem).