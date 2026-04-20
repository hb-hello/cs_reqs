%%%%% for unsupported requirements, we put 'unsupported' and assume they are satisfied.
unsupported_prereq.     %%% assume unsupported prereqs are satisfied
unsupported_coreq.      %%% assume unsupported coreqs are satisfied
unsupported_pre_or_coreq. %%% assume unsupported pre_or_coreqs are satisfied
unsupported_anti_req.   %%% assume unsupported anti-reqs are satisfied
credits("CSE 101", 4).
has_anti_req("CSE 101").
anti_req("CSE 101", Sem) :- offered("CSE 101", Sem), not passed_before("CSE 114", Sem),not passed_before("CSE 160", Sem).
has_prereq("CSE 101").
prereq("CSE 101", Sem) :- offered("CSE 101", Sem), unsupported_prereq.
credits("CSE 102", 3).
credits("CSE 110", 3).
has_prereq("CSE 110").
prereq("CSE 110", Sem) :- offered("CSE 110", Sem), unsupported_prereq.
credits("CSE 113", 4).
has_prereq("CSE 113").
prereq("CSE 113", Sem) :- offered("CSE 113", Sem), taken_before("AMS 151", Sem).
prereq("CSE 113", Sem) :- offered("CSE 113", Sem), taken_before("MAT 125", Sem).
prereq("CSE 113", Sem) :- offered("CSE 113", Sem), taken_before("MAT 131", Sem).
credits("CSE 114", 4).
has_prereq("CSE 114").
prereq("CSE 114", Sem) :- offered("CSE 114", Sem), unsupported_prereq.
credits("CSE 130", 3).
has_prereq("CSE 130").
prereq("CSE 130", Sem) :- offered("CSE 130", Sem), unsupported_prereq.
credits("CSE 150", 4).
has_prereq("CSE 150").
prereq("CSE 150", Sem) :- offered("CSE 150", Sem), unsupported_prereq,unsupported_prereq.
credits("CSE 160", 3).
has_coreq("CSE 160").
coreq("CSE 160", Sem) :- offered("CSE 160", Sem), taken_together("CSE 161", Sem).
has_prereq("CSE 160").
prereq("CSE 160", Sem) :- offered("CSE 160", Sem), unsupported_prereq.
credits("CSE 161", 1).
has_coreq("CSE 161").
coreq("CSE 161", Sem) :- offered("CSE 161", Sem), taken_together("CSE 160", Sem).
credits("CSE 190", 3).
credits("CSE 191", 3).
credits("CSE 192", 3).
credits("CSE 214", 4).
has_prereq("CSE 214").
prereq("CSE 214", Sem) :- offered("CSE 214", Sem), passed_before("CSE 114", Sem).
credits("CSE 215", 4).
has_prereq("CSE 215").
prereq("CSE 215", Sem) :- offered("CSE 215", Sem), taken_before("AMS 151", Sem).
prereq("CSE 215", Sem) :- offered("CSE 215", Sem), taken_before("MAT 125", Sem).
prereq("CSE 215", Sem) :- offered("CSE 215", Sem), taken_before("MAT 131", Sem).
credits("CSE 216", 4).
has_prereq("CSE 216").
prereq("CSE 216", Sem) :- offered("CSE 216", Sem), passed_before("CSE 214", Sem),major("CSE").
credits("CSE 220", 4).
has_prereq("CSE 220").
prereq("CSE 220", Sem) :- offered("CSE 220", Sem), unsupported_prereq.
credits("CSE 230", 3).
has_prereq("CSE 230").
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("CSE 130", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("CSE 220", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("ESE 124", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("ESG 111", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("BME 120", Sem).
prereq("CSE 230", Sem) :- offered("CSE 230", Sem), taken_before("MEC 102", Sem).
credits("CSE 260", 3).
has_coreq("CSE 260").
coreq("CSE 260", Sem) :- offered("CSE 260", Sem), taken_together("CSE 261", Sem).
has_prereq("CSE 260").
prereq("CSE 260", Sem) :- offered("CSE 260", Sem), taken_before("CSE 160", Sem).
credits("CSE 261", 1).
has_coreq("CSE 261").
coreq("CSE 261", Sem) :- offered("CSE 261", Sem), taken_together("CSE 260", Sem).
credits("CSE 300", 3).
has_prereq("CSE 300").
prereq("CSE 300", Sem) :- offered("CSE 300", Sem), taken_before("WRT 102", Sem),major("CSE"; "ISE"; "DAS"),standing("U3"; "U4").
credits("CSE 301", 3).
has_prereq("CSE 301").
prereq("CSE 301", Sem) :- offered("CSE 301", Sem), standing("U2").
prereq("CSE 301", Sem) :- offered("CSE 301", Sem), standing("U3").
prereq("CSE 301", Sem) :- offered("CSE 301", Sem), standing("U4").
credits("CSE 303", 3).
has_prereq("CSE 303").
prereq("CSE 303", Sem) :- offered("CSE 303", Sem), passed_before(("CSE 160"; "CSE 214"), Sem),passed_before(("CSE 150"; "CSE 215"), Sem),major("CSE").
credits("CSE 304", 3).
has_prereq("CSE 304").
prereq("CSE 304", Sem) :- offered("CSE 304", Sem), passed_before(("CSE 216"; "CSE 260"), Sem),passed_before("CSE 220", Sem).
credits("CSE 305", 3).
has_prereq("CSE 305").
prereq("CSE 305", Sem) :- offered("CSE 305", Sem), passed_before("CSE 214", Sem),passed_before(("CSE 216"; "CSE 260"), Sem),major("CSE"; "DAS").
credits("CSE 306", 3).
has_prereq("CSE 306").
prereq("CSE 306", Sem) :- offered("CSE 306", Sem), passed_before(("CSE 320"; "ESE 280"), Sem),major("CSE"; "ECE").
credits("CSE 307", 3).
has_prereq("CSE 307").
prereq("CSE 307", Sem) :- offered("CSE 307", Sem), passed_before("CSE 214", Sem),passed_before(("CSE 216"; "CSE 260"), Sem),major("CSE"; "DAS").
credits("CSE 310", 3).
has_prereq("CSE 310").
prereq("CSE 310", Sem) :- offered("CSE 310", Sem), passed_before(("CSE 214"; "CSE 260"), Sem),passed_before(("CSE 220"; "ISE 218"), Sem),major("CSE"; "ISE").
credits("CSE 311", 3).
has_prereq("CSE 311").
prereq("CSE 311", Sem) :- offered("CSE 311", Sem), taken_before(("CSE 214"; "CSE 230"; "CSE 260"; "ISE 208"), Sem),major("ISE"; "CSE").
credits("CSE 312", 3).
has_prereq("CSE 312").
prereq("CSE 312", Sem) :- offered("CSE 312", Sem), major("CSE"; "ISE"; "DAS"),standing("U3"; "U4"),unsupported_prereq.
credits("CSE 316", 3).
has_prereq("CSE 316").
prereq("CSE 316", Sem) :- offered("CSE 316", Sem), passed_before(("CSE 214"; "CSE 260"), Sem),passed_before(("CSE 216"; "CSE 307"), Sem),major("CSE").
credits("CSE 320", 3).
has_prereq("CSE 320").
prereq("CSE 320", Sem) :- offered("CSE 320", Sem), passed_before("CSE 220", Sem),major("CSE").
credits("CSE 323", 3).
has_prereq("CSE 323").
prereq("CSE 323", Sem) :- offered("CSE 323", Sem), taken_before("CSE 214", Sem).
prereq("CSE 323", Sem) :- offered("CSE 323", Sem), taken_before("CSE 230", Sem).
prereq("CSE 323", Sem) :- offered("CSE 323", Sem), taken_before("CSE 260", Sem).
prereq("CSE 323", Sem) :- offered("CSE 323", Sem), taken_before("ISE 208", Sem).
credits("CSE 325", 3).
has_prereq("CSE 325").
prereq("CSE 325", Sem) :- offered("CSE 325", Sem), taken_before("CSE 110", Sem).
prereq("CSE 325", Sem) :- offered("CSE 325", Sem), taken_before("CSE 101", Sem).
prereq("CSE 325", Sem) :- offered("CSE 325", Sem), taken_before("CSE 114", Sem).
credits("CSE 327", 3).
has_prereq("CSE 327").
prereq("CSE 327", Sem) :- offered("CSE 327", Sem), taken_before(("CSE 214"; "CSE 230"; "CSE 260"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem),major("CSE"; "ISE"; "DAS").
credits("CSE 328", 3).
has_prereq("CSE 328").
prereq("CSE 328", Sem) :- offered("CSE 328", Sem), passed_before("CSE 220", Sem),major("CSE"; "DAS").
credits("CSE 331", 3).
has_prereq("CSE 331").
prereq("CSE 331", Sem) :- offered("CSE 331", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 332", 3).
has_prereq("CSE 332").
prereq("CSE 332", Sem) :- offered("CSE 332", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),taken_before(("MAT 211"; "AMS 210"), Sem),taken_before(("AMS 110"; "AMS 310"), Sem),major("CSE"; "ISE"; "DAS").
credits("CSE 333", 3).
has_prereq("CSE 333").
prereq("CSE 333", Sem) :- offered("CSE 333", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 334", 3).
has_prereq("CSE 334").
prereq("CSE 334", Sem) :- offered("CSE 334", Sem), standing("U2"; "U3"; "U4"),major("CSE"; "ISE").
credits("CSE 336", 3).
has_prereq("CSE 336").
prereq("CSE 336", Sem) :- offered("CSE 336", Sem), passed_before(("CSE 214"; "CSE 260"), Sem),major("CSE").
credits("CSE 337", 3).
has_prereq("CSE 337").
prereq("CSE 337", Sem) :- offered("CSE 337", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE"; "DAS"),standing("U3"; "U4").
credits("CSE 350", 4).
has_prereq("CSE 350").
prereq("CSE 350", Sem) :- offered("CSE 350", Sem), taken_before(("CSE 113"; "CSE 150"; "CSE 215"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem),unsupported_prereq.
credits("CSE 351", 3).
has_prereq("CSE 351").
prereq("CSE 351", Sem) :- offered("CSE 351", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),taken_before("AMS 310", Sem),major("CSE"; "DAS").
credits("CSE 352", 3).
has_prereq("CSE 352").
prereq("CSE 352", Sem) :- offered("CSE 352", Sem), taken_before(("CSE 316"; "CSE 351"), Sem),major("CSE"; "DAS").
credits("CSE 353", 3).
has_pre_or_coreq("CSE 353").
pre_or_coreq("CSE 353", Sem) :- offered("CSE 353", Sem), taken_before_or_together("AMS 310", Sem).
pre_or_coreq("CSE 353", Sem) :- offered("CSE 353", Sem), taken_before_or_together("AMS 311", Sem).
pre_or_coreq("CSE 353", Sem) :- offered("CSE 353", Sem), taken_before_or_together("AMS 412", Sem).
has_prereq("CSE 353").
prereq("CSE 353", Sem) :- offered("CSE 353", Sem), taken_before(("CSE 316"; "CSE 351"), Sem),major("CSE"; "DAS").
credits("CSE 354", 3).
has_prereq("CSE 354").
prereq("CSE 354", Sem) :- offered("CSE 354", Sem), taken_before(("CSE 316"; "CSE 351"), Sem),major("CSE"; "DAS").
credits("CSE 355", 3).
has_prereq("CSE 355").
prereq("CSE 355", Sem) :- offered("CSE 355", Sem), taken_before("AMS 301", Sem),unsupported_prereq.
credits("CSE 356", 3).
has_prereq("CSE 356").
prereq("CSE 356", Sem) :- offered("CSE 356", Sem), passed_before("CSE 316", Sem),passed_before("CSE 320", Sem),major("CSE").
credits("CSE 357", 3).
has_prereq("CSE 357").
prereq("CSE 357", Sem) :- offered("CSE 357", Sem), passed_before(("CSE 316"; "CSE 351"), Sem),passed_before("AMS 310", Sem),major("CSE"; "DAS").
credits("CSE 360", 3).
has_prereq("CSE 360").
prereq("CSE 360", Sem) :- offered("CSE 360", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 361", 3).
has_prereq("CSE 361").
prereq("CSE 361", Sem) :- offered("CSE 361", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 362", 3).
has_prereq("CSE 362").
prereq("CSE 362", Sem) :- offered("CSE 362", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 363", 3).
has_prereq("CSE 363").
prereq("CSE 363", Sem) :- offered("CSE 363", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 364", 3).
has_prereq("CSE 364").
prereq("CSE 364", Sem) :- offered("CSE 364", Sem), taken_before("CSE 334", Sem).
prereq("CSE 364", Sem) :- offered("CSE 364", Sem), taken_before("ISE 334", Sem).
credits("CSE 366", 3).
has_prereq("CSE 366").
prereq("CSE 366", Sem) :- offered("CSE 366", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),taken_before(("MAT 211"; "AMS 210"), Sem),major("CSE"; "ISE").
credits("CSE 370", 3).
has_prereq("CSE 370").
prereq("CSE 370", Sem) :- offered("CSE 370", Sem), taken_before("CSE 310", Sem),major("CSE").
credits("CSE 371", 3).
has_prereq("CSE 371").
prereq("CSE 371", Sem) :- offered("CSE 371", Sem), taken_before("CSE 113", Sem).
prereq("CSE 371", Sem) :- offered("CSE 371", Sem), taken_before("CSE 150", Sem).
prereq("CSE 371", Sem) :- offered("CSE 371", Sem), taken_before("CSE 215", Sem).
prereq("CSE 371", Sem) :- offered("CSE 371", Sem), taken_before("MAT 200", Sem).
prereq("CSE 371", Sem) :- offered("CSE 371", Sem), taken_before("MAT 250", Sem).
credits("CSE 373", 3).
has_prereq("CSE 373").
prereq("CSE 373", Sem) :- offered("CSE 373", Sem), passed_before(("CSE 113"; "CSE 150"; "CSE 215"; "MAT 200"; "MAT 250"), Sem),passed_before(("MAT 211"; "AMS 210"), Sem),passed_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "MAT"; "DAS").
credits("CSE 376", 3).
has_prereq("CSE 376").
prereq("CSE 376", Sem) :- offered("CSE 376", Sem), passed_before("CSE 320", Sem),major("CSE").
credits("CSE 377", 3).
has_prereq("CSE 377").
prereq("CSE 377", Sem) :- offered("CSE 377", Sem), taken_before(("AMS 161"; "MAT 127"; "MAT 132"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem).
credits("CSE 378", 3).
has_prereq("CSE 378").
prereq("CSE 378", Sem) :- offered("CSE 378", Sem), taken_before(("AMS 161"; "MAT 127"; "MAT 132"), Sem),taken_before(("AMS 210"; "MAT 211"; "MEC 262"), Sem).
credits("CSE 380", 3).
has_prereq("CSE 380").
prereq("CSE 380", Sem) :- offered("CSE 380", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 381", 3).
has_prereq("CSE 381").
prereq("CSE 381", Sem) :- offered("CSE 381", Sem), taken_before("CSE 220", Sem),major("CSE").
credits("CSE 385", 4).
has_prereq("CSE 385").
prereq("CSE 385", Sem) :- offered("CSE 385", Sem), taken_before(("CSE 113"; "CSE 150"; "CSE 215"; "MAT 200"; "MAT 250"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem),taken_before(("CSE 214"; "CSE 260"), Sem),unsupported_prereq.
credits("CSE 390", 3).
has_prereq("CSE 390").
prereq("CSE 390", Sem) :- offered("CSE 390", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 391", 3).
has_prereq("CSE 391").
prereq("CSE 391", Sem) :- offered("CSE 391", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 392", 3).
has_prereq("CSE 392").
prereq("CSE 392", Sem) :- offered("CSE 392", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 393", 3).
has_prereq("CSE 393").
prereq("CSE 393", Sem) :- offered("CSE 393", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 394", 3).
has_prereq("CSE 394").
prereq("CSE 394", Sem) :- offered("CSE 394", Sem), taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
credits("CSE 416", 3).
has_prereq("CSE 416").
prereq("CSE 416", Sem) :- offered("CSE 416", Sem), passed_before("CSE 316", Sem),standing("U4"),major("CSE").
credits("CSE 475", 3).
has_prereq("CSE 475").
prereq("CSE 475", Sem) :- offered("CSE 475", Sem), unsupported_prereq,unsupported_prereq,unsupported_prereq.
credits("CSE 487", 0).
credits("CSE 487", 1).
credits("CSE 487", 2).
credits("CSE 487", 3).
has_prereq("CSE 487").
prereq("CSE 487", Sem) :- offered("CSE 487", Sem), permission.
credits("CSE 488", 3).
has_prereq("CSE 488").
prereq("CSE 488", Sem) :- offered("CSE 488", Sem), major("CSE"),standing("U3"; "U4"),permission.
credits("CSE 495", 3).
has_prereq("CSE 495").
prereq("CSE 495", Sem) :- offered("CSE 495", Sem), unsupported_prereq,permission.
credits("CSE 496", 3).
has_prereq("CSE 496").
prereq("CSE 496", Sem) :- offered("CSE 496", Sem), taken_before("CSE 495", Sem),permission.
credits("AMS 151", 3).
has_prereq("AMS 151").
prereq("AMS 151", Sem) :- offered("AMS 151", Sem), passed_before_grade("MAT 123", "B", Sem).
credits("AMS 161", 3).
has_prereq("AMS 161").
prereq("AMS 161", Sem) :- offered("AMS 161", Sem), passed_before("AMS 151", Sem).
prereq("AMS 161", Sem) :- offered("AMS 161", Sem), passed_before("MAT 131", Sem).
credits("AMS 210", 3).
has_prereq("AMS 210").
prereq("AMS 210", Sem) :- offered("AMS 210", Sem), taken_before("AMS 151", Sem).
prereq("AMS 210", Sem) :- offered("AMS 210", Sem), taken_before("MAT 131", Sem).
prereq("AMS 210", Sem) :- offered("AMS 210", Sem), taken_together("MAT 126").
credits("AMS 301", 3).
has_prereq("AMS 301").
prereq("AMS 301", Sem) :- offered("AMS 301", Sem), taken_before("AMS 210", Sem).
prereq("AMS 301", Sem) :- offered("AMS 301", Sem), taken_before("MAT 211", Sem).
prereq("AMS 301", Sem) :- offered("AMS 301", Sem), taken_before("AMS 361", Sem).
prereq("AMS 301", Sem) :- offered("AMS 301", Sem), taken_before("MAT 303", Sem).
credits("AMS 310", 3).
has_prereq("AMS 310").
prereq("AMS 310", Sem) :- offered("AMS 310", Sem), taken_before("AMS 161", Sem).
prereq("AMS 310", Sem) :- offered("AMS 310", Sem), taken_before("MAT 132", Sem).
prereq("AMS 310", Sem) :- offered("AMS 310", Sem), taken_before("MAT 127", Sem).
credits("AMS 311", 3).
has_coreq("AMS 311").
coreq("AMS 311", Sem) :- offered("AMS 311", Sem), taken_together("MAT 203", Sem).
coreq("AMS 311", Sem) :- offered("AMS 311", Sem), taken_together("AMS 261", Sem).
has_prereq("AMS 311").
prereq("AMS 311", Sem) :- offered("AMS 311", Sem), taken_before("AMS 301", Sem),taken_before("AMS 310", Sem).
prereq("AMS 311", Sem) :- offered("AMS 311", Sem), permission.
credits("MAT 123", 3).
has_prereq("MAT 123").
prereq("MAT 123", Sem) :- offered("MAT 123", Sem), unsupported_prereq.
credits("MAT 125", 3).
has_prereq("MAT 125").
prereq("MAT 125", Sem) :- offered("MAT 125", Sem), passed_before("MAT 123", Sem).
prereq("MAT 125", Sem) :- offered("MAT 125", Sem), taken_together("MAT 130").
credits("MAT 126", 3).
has_prereq("MAT 126").
prereq("MAT 126", Sem) :- offered("MAT 126", Sem), passed_before("MAT 125", Sem).
prereq("MAT 126", Sem) :- offered("MAT 126", Sem), passed_before("MAT 131", Sem).
prereq("MAT 126", Sem) :- offered("MAT 126", Sem), passed_before("MAT 141", Sem).
prereq("MAT 126", Sem) :- offered("MAT 126", Sem), passed_before("AMS 151", Sem).
credits("MAT 127", 3).
has_prereq("MAT 127").
prereq("MAT 127", Sem) :- offered("MAT 127", Sem), passed_before("MAT 126", Sem).
credits("MAT 131", 4).
has_prereq("MAT 131").
prereq("MAT 131", Sem) :- offered("MAT 131", Sem), passed_before_grade("MAT 123", "B", Sem).
credits("MAT 132", 4).
has_prereq("MAT 132").
prereq("MAT 132", Sem) :- offered("MAT 132", Sem), passed_before("AMS 151", Sem).
prereq("MAT 132", Sem) :- offered("MAT 132", Sem), passed_before("MAT 131", Sem).
prereq("MAT 132", Sem) :- offered("MAT 132", Sem), passed_before("MAT 141", Sem).
credits("MAT 211", 3).
has_prereq("MAT 211").
prereq("MAT 211", Sem) :- offered("MAT 211", Sem), passed_before("AMS 151", Sem).
prereq("MAT 211", Sem) :- offered("MAT 211", Sem), passed_before("MAT 131", Sem).
prereq("MAT 211", Sem) :- offered("MAT 211", Sem), passed_before("MAT 141", Sem).
prereq("MAT 211", Sem) :- offered("MAT 211", Sem), taken_together("MAT 126").
credits("BIO 201", 3).
has_prereq("BIO 201").
prereq("BIO 201", Sem) :- offered("BIO 201", Sem), unsupported_prereq.
credits("BIO 202", 3).
has_prereq("BIO 202").
prereq("BIO 202", Sem) :- offered("BIO 202", Sem), passed_before("CHE 129", Sem).
prereq("BIO 202", Sem) :- offered("BIO 202", Sem), passed_before("CHE 131", Sem).
prereq("BIO 202", Sem) :- offered("BIO 202", Sem), taken_together("CHE 152").
credits("BIO 203", 3).
has_prereq("BIO 203").
prereq("BIO 203", Sem) :- offered("BIO 203", Sem), taken_before("CHE 129", Sem).
prereq("BIO 203", Sem) :- offered("BIO 203", Sem), taken_before("CHE 131", Sem).
prereq("BIO 203", Sem) :- offered("BIO 203", Sem), taken_together("CHE 152").
credits("BIO 204", 2).
has_prereq("BIO 204").
prereq("BIO 204", Sem) :- offered("BIO 204", Sem), taken_before("CHE 129", Sem),taken_before("CHE 131", Sem).
prereq("BIO 204", Sem) :- offered("BIO 204", Sem), taken_together("CHE 152").
credits("CHE 131", 4).
has_coreq("CHE 131").
coreq("CHE 131", Sem) :- offered("CHE 131", Sem), unsupported_coreq.
has_prereq("CHE 131").
prereq("CHE 131", Sem) :- offered("CHE 131", Sem), unsupported_prereq.
credits("CHE 132", 4).
has_pre_or_coreq("CHE 132").
pre_or_coreq("CHE 132", Sem) :- offered("CHE 132", Sem), unsupported_pre_or_coreq,unsupported_pre_or_coreq.
has_prereq("CHE 132").
prereq("CHE 132", Sem) :- offered("CHE 132", Sem), passed_before("CHE 129", Sem).
prereq("CHE 132", Sem) :- offered("CHE 132", Sem), passed_before("CHE 131", Sem).
credits("CHE 133", 1).
credits("CHE 152", 4).
has_prereq("CHE 152").
prereq("CHE 152", Sem) :- offered("CHE 152", Sem), unsupported_prereq,unsupported_prereq.
credits("CHE 154", 2).
has_coreq("CHE 154").
coreq("CHE 154", Sem) :- offered("CHE 154", Sem), taken_together("CHE 152", Sem).
credits("CHE 321", 4).
has_prereq("CHE 321").
prereq("CHE 321", Sem) :- offered("CHE 321", Sem), passed_before("CHE 132", Sem).
credits("CHE 322", 4).
has_prereq("CHE 322").
prereq("CHE 322", Sem) :- offered("CHE 322", Sem), passed_before("CHE 321", Sem).
credits("CHE 331", 4).
has_coreq("CHE 331").
coreq("CHE 331", Sem) :- offered("CHE 331", Sem), taken_together("CHE 383", Sem).
has_prereq("CHE 331").
prereq("CHE 331", Sem) :- offered("CHE 331", Sem), passed_before("CHE 152", Sem).
credits("CHE 332", 4).
has_prereq("CHE 332").
prereq("CHE 332", Sem) :- offered("CHE 332", Sem), passed_before("CHE 331", Sem).
credits("PHY 125", 3).
has_prereq("PHY 125").
prereq("PHY 125", Sem) :- offered("PHY 125", Sem), taken_before("MAT 125", Sem).
credits("PHY 126", 3).
has_prereq("PHY 126").
prereq("PHY 126", Sem) :- offered("PHY 126", Sem), passed_before("PHY 125", Sem).
prereq("PHY 126", Sem) :- offered("PHY 126", Sem), passed_before("PHY 131", Sem).
prereq("PHY 126", Sem) :- offered("PHY 126", Sem), passed_before("PHY 141", Sem).
credits("PHY 127", 3).
has_prereq("PHY 127").
prereq("PHY 127", Sem) :- offered("PHY 127", Sem), passed_before("PHY 125", Sem).
prereq("PHY 127", Sem) :- offered("PHY 127", Sem), passed_before("PHY 131", Sem).
prereq("PHY 127", Sem) :- offered("PHY 127", Sem), passed_before("PHY 141", Sem).
credits("PHY 131", 3).
has_prereq("PHY 131").
prereq("PHY 131", Sem) :- offered("PHY 131", Sem), unsupported_prereq.
credits("PHY 132", 3).
has_prereq("PHY 132").
prereq("PHY 132", Sem) :- offered("PHY 132", Sem), passed_before("PHY 131", Sem).
prereq("PHY 132", Sem) :- offered("PHY 132", Sem), passed_before("PHY 141", Sem).
credits("PHY 133", 1).
has_pre_or_coreq("PHY 133").
pre_or_coreq("PHY 133", Sem) :- offered("PHY 133", Sem), taken_before_or_together("PHY 125", Sem),taken_before_or_together("PHY 126", Sem).
pre_or_coreq("PHY 133", Sem) :- offered("PHY 133", Sem), taken_before_or_together("PHY 131", Sem).
pre_or_coreq("PHY 133", Sem) :- offered("PHY 133", Sem), taken_before_or_together("PHY 141", Sem).
credits("PHY 134", 1).
has_prereq("PHY 134").
prereq("PHY 134", Sem) :- offered("PHY 134", Sem), passed_before("PHY 133", Sem).
credits("PHY 141", 3).
credits("PHY 142", 3).
has_prereq("PHY 142").
prereq("PHY 142", Sem) :- offered("PHY 142", Sem), passed_before("PHY 141", Sem).
prereq("PHY 142", Sem) :- offered("PHY 142", Sem), permission.
credits("PHY 251", 3).
has_pre_or_coreq("PHY 251").
pre_or_coreq("PHY 251", Sem) :- offered("PHY 251", Sem), taken_before_or_together("MAT 203", Sem).
pre_or_coreq("PHY 251", Sem) :- offered("PHY 251", Sem), taken_before_or_together("MAT 205", Sem).
pre_or_coreq("PHY 251", Sem) :- offered("PHY 251", Sem), taken_before_or_together("AMS 261", Sem).
pre_or_coreq("PHY 251", Sem) :- offered("PHY 251", Sem), taken_before_or_together("MAT 307", Sem).
has_prereq("PHY 251").
prereq("PHY 251", Sem) :- offered("PHY 251", Sem), aux_or_1(Sem),taken_before("PHY 134", Sem),passed_before(("MAT 126"; "MAT 132"; "MAT 142"; "MAT 171"; "AMS 161"), Sem).
credits("PHY 252", 1).
has_pre_or_coreq("PHY 252").
pre_or_coreq("PHY 252", Sem) :- offered("PHY 252", Sem), taken_before_or_together("PHY 251", Sem).
credits("GEO 102", 3).
credits("GEO 103", 3).
credits("GEO 112", 1).
credits("GEO 122", 4).
credits("AST 203", 4).
has_prereq("AST 203").
prereq("AST 203", Sem) :- offered("AST 203", Sem), taken_before("PHY 125", Sem).
prereq("AST 203", Sem) :- offered("AST 203", Sem), taken_before("PHY 133", Sem).
prereq("AST 203", Sem) :- offered("AST 203", Sem), taken_before("PHY 131", Sem).
prereq("AST 203", Sem) :- offered("AST 203", Sem), taken_before("PHY 141", Sem).
credits("AST 205", 3).
has_prereq("AST 205").
prereq("AST 205", Sem) :- offered("AST 205", Sem), taken_before("PHY 125", Sem).
prereq("AST 205", Sem) :- offered("AST 205", Sem), taken_before("PHY 133", Sem).
prereq("AST 205", Sem) :- offered("AST 205", Sem), taken_before("PHY 131", Sem).
prereq("AST 205", Sem) :- offered("AST 205", Sem), taken_before("PHY 141", Sem).
credits("WRT 101", 3).
has_prereq("WRT 101").
prereq("WRT 101", Sem) :- offered("WRT 101", Sem), unsupported_prereq.
credits("WRT 102", 3).
has_prereq("WRT 102").
prereq("WRT 102", Sem) :- offered("WRT 102", Sem), passed_before("WRT 101", Sem).
credits("AMS 110", 3).
has_anti_req("AMS 110").
anti_req("AMS 110", Sem) :- offered("AMS 110", Sem), not passed_before("AMS 310", Sem),not passed_before("MAT 203", Sem).
has_prereq("AMS 110").
prereq("AMS 110", Sem) :- offered("AMS 110", Sem), taken_before("AMS 151", Sem).
prereq("AMS 110", Sem) :- offered("AMS 110", Sem), taken_before("MAT 125", Sem).
prereq("AMS 110", Sem) :- offered("AMS 110", Sem), taken_before("MAT 131", Sem).
credits("AMS 261", 4).
has_prereq("AMS 261").
prereq("AMS 261", Sem) :- offered("AMS 261", Sem), taken_before("AMS 161", Sem).
prereq("AMS 261", Sem) :- offered("AMS 261", Sem), taken_before("MAT 127", Sem).
prereq("AMS 261", Sem) :- offered("AMS 261", Sem), taken_before("MAT 132", Sem).
credits("AMS 361", 4).
has_prereq("AMS 361").
prereq("AMS 361", Sem) :- offered("AMS 361", Sem), taken_before("AMS 161", Sem).
prereq("AMS 361", Sem) :- offered("AMS 361", Sem), taken_before("MAT 127", Sem).
prereq("AMS 361", Sem) :- offered("AMS 361", Sem), taken_before("MAT 132", Sem).
credits("AMS 412", 3).
has_prereq("AMS 412").
prereq("AMS 412", Sem) :- offered("AMS 412", Sem), taken_before("AMS 311", Sem).
credits("MAT 130", 1).
has_prereq("MAT 130").
prereq("MAT 130", Sem) :- offered("MAT 130", Sem), taken_before("MAT 122", Sem).
prereq("MAT 130", Sem) :- offered("MAT 130", Sem), permission.
credits("MAT 200", 3).
has_prereq("MAT 200").
prereq("MAT 200", Sem) :- offered("MAT 200", Sem), unsupported_prereq.
credits("MAT 203", 4).
has_prereq("MAT 203").
prereq("MAT 203", Sem) :- offered("MAT 203", Sem), passed_before("MAT 127", Sem).
prereq("MAT 203", Sem) :- offered("MAT 203", Sem), passed_before("MAT 132", Sem).
prereq("MAT 203", Sem) :- offered("MAT 203", Sem), passed_before("MAT 142", Sem).
prereq("MAT 203", Sem) :- offered("MAT 203", Sem), passed_before("AMS 161", Sem).
credits("MAT 250", 4).
has_prereq("MAT 250").
prereq("MAT 250", Sem) :- offered("MAT 250", Sem), taken_before("MAT 131", Sem).
credits("MAT 303", 4).
has_prereq("MAT 303").
prereq("MAT 303", Sem) :- offered("MAT 303", Sem), passed_before("MAT 127", Sem).
prereq("MAT 303", Sem) :- offered("MAT 303", Sem), passed_before("MAT 132", Sem).
prereq("MAT 303", Sem) :- offered("MAT 303", Sem), passed_before("MAT 142", Sem).
prereq("MAT 303", Sem) :- offered("MAT 303", Sem), passed_before("AMS 161", Sem).
credits("MAT 307", 4).
has_prereq("MAT 307").
prereq("MAT 307", Sem) :- offered("MAT 307", Sem), taken_before("MAT 127", Sem).
prereq("MAT 307", Sem) :- offered("MAT 307", Sem), taken_before("MAT 132", Sem).
credits("CHE 129", 4).
has_coreq("CHE 129").
coreq("CHE 129", Sem) :- offered("CHE 129", Sem), taken_together("CHE 130", Sem),taken_together("MAT 123", Sem).
has_prereq("CHE 129").
prereq("CHE 129", Sem) :- offered("CHE 129", Sem), unsupported_prereq.
credits("CHE 383", 2).
has_coreq("CHE 383").
coreq("CHE 383", Sem) :- offered("CHE 383", Sem), taken_together("CHE 331", Sem).
has_prereq("CHE 383").
prereq("CHE 383", Sem) :- offered("CHE 383", Sem), taken_before("CHE 154", Sem).
credits("PHY 122", 4).
has_pre_or_coreq("PHY 122").
pre_or_coreq("PHY 122", Sem) :- offered("PHY 122", Sem), taken_before_or_together("CHE 132", Sem).
pre_or_coreq("PHY 122", Sem) :- offered("PHY 122", Sem), taken_before_or_together("CHE 152", Sem).
has_prereq("PHY 122").
prereq("PHY 122", Sem) :- offered("PHY 122", Sem), passed_before("PHY 121", Sem).
credits("CHE 130", 1).
has_coreq("CHE 130").
coreq("CHE 130", Sem) :- offered("CHE 130", Sem), taken_together("CHE 129", Sem),taken_together("MAT 123", Sem).
aux_or_1(Sem) :- taken_before("PHY 122", Sem),taken_before("PHY 124", Sem).
aux_or_1(Sem) :- taken_before("PHY 126", Sem),taken_before("PHY 127", Sem).
aux_or_1(Sem) :- taken_before("PHY 132", Sem).
aux_or_1(Sem) :- taken_before("PHY 142", Sem).