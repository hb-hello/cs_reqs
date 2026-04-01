%%%%% for unsupported requirements, we put 'unsupported' and assume they are satisfied.
unsupported_prereq.     %%% assume unsupported prereqs are satisfied
unsupported_coreq.      %%% assume unsupported coreqs are satisfied
course("CSE 101", 4).
has_prereq("CSE 101").
prereq("CSE 101", Sem) :- semester(Sem),unsupported_prereq.
has_anti_req("CSE 101").
anti_req("CSE 101", Sem) :- semester(Sem), taken_before("CSE 114", Sem).
anti_req("CSE 101", Sem) :- semester(Sem), taken_before("CSE 160", Sem).
course("CSE 102", 3).
course("CSE 110", 3).
has_prereq("CSE 110").
prereq("CSE 110", Sem) :- semester(Sem),unsupported_prereq.
course("CSE 113", 4).
has_prereq("CSE 113").
prereq("CSE 113", Sem) :- semester(Sem), taken_before("AMS 151", Sem).
prereq("CSE 113", Sem) :- semester(Sem), taken_before("MAT 125", Sem).
prereq("CSE 113", Sem) :- semester(Sem), taken_before("MAT 131", Sem).
course("CSE 114", 4).
has_prereq("CSE 114").
prereq("CSE 114", Sem) :- semester(Sem),unsupported_prereq.
course("CSE 130", 3).
has_prereq("CSE 130").
prereq("CSE 130", Sem) :- semester(Sem),unsupported_prereq.
course("CSE 150", 4).
has_prereq("CSE 150").
prereq("CSE 150", Sem) :- semester(Sem),unsupported_prereq,unsupported_prereq.
course("CSE 160", 3).
has_prereq("CSE 160").
prereq("CSE 160", Sem) :- semester(Sem),unsupported_prereq.
has_coreq("CSE 160").
coreq("CSE 160", Sem) :- semester(Sem),taken_same("CSE 161", Sem).
course("CSE 161", 1).
has_coreq("CSE 161").
coreq("CSE 161", Sem) :- semester(Sem),taken_same("CSE 160", Sem).
course("CSE 190", 3).
course("CSE 191", 3).
course("CSE 192", 3).
course("CSE 214", 4).
has_prereq("CSE 214").
prereq("CSE 214", Sem) :- semester(Sem),passed_before(("CSE 114","C"), Sem).
course("CSE 215", 4).
has_prereq("CSE 215").
prereq("CSE 215", Sem) :- semester(Sem), taken_before("AMS 151", Sem).
prereq("CSE 215", Sem) :- semester(Sem), taken_before("MAT 125", Sem).
prereq("CSE 215", Sem) :- semester(Sem), taken_before("MAT 131", Sem).
course("CSE 216", 4).
has_prereq("CSE 216").
prereq("CSE 216", Sem) :- semester(Sem),passed_before(("CSE 214","C"), Sem),major("CSE").
course("CSE 220", 4).
has_prereq("CSE 220").
prereq("CSE 220", Sem) :- semester(Sem),unsupported_prereq.
course("CSE 230", 3).
has_prereq("CSE 230").
prereq("CSE 230", Sem) :- semester(Sem), taken_before("CSE 130", Sem).
prereq("CSE 230", Sem) :- semester(Sem), taken_before("CSE 220", Sem).
prereq("CSE 230", Sem) :- semester(Sem), taken_before("ESE 124", Sem).
prereq("CSE 230", Sem) :- semester(Sem), taken_before("ESG 111", Sem).
prereq("CSE 230", Sem) :- semester(Sem), taken_before("BME 120", Sem).
prereq("CSE 230", Sem) :- semester(Sem), taken_before("MEC 102", Sem).
course("CSE 260", 3).
has_prereq("CSE 260").
prereq("CSE 260", Sem) :- semester(Sem),taken_before("CSE 160", Sem).
has_coreq("CSE 260").
coreq("CSE 260", Sem) :- semester(Sem),taken_same("CSE 261", Sem).
course("CSE 261", 1).
has_coreq("CSE 261").
coreq("CSE 261", Sem) :- semester(Sem),taken_same("CSE 260", Sem).
course("CSE 300", 3).
has_prereq("CSE 300").
prereq("CSE 300", Sem) :- semester(Sem),taken_before("WRT 102", Sem),major("CSE"; "ISE"; "DAS"),standing("U3"; "U4").
course("CSE 301", 3).
has_prereq("CSE 301").
prereq("CSE 301", Sem) :- semester(Sem), standing("U2").
prereq("CSE 301", Sem) :- semester(Sem), standing("U3").
prereq("CSE 301", Sem) :- semester(Sem), standing("U4").
course("CSE 303", 3).
has_prereq("CSE 303").
prereq("CSE 303", Sem) :- semester(Sem),passed_before(("CSE 160","C"; "CSE 214","C"), Sem),passed_before(("CSE 150","C"; "CSE 215","C"), Sem),major("CSE").
course("CSE 304", 3).
has_prereq("CSE 304").
prereq("CSE 304", Sem) :- semester(Sem),passed_before(("CSE 216","C"; "CSE 260","C"), Sem),passed_before(("CSE 220","C"), Sem).
course("CSE 305", 3).
has_prereq("CSE 305").
prereq("CSE 305", Sem) :- semester(Sem),passed_before(("CSE 214","C"), Sem),passed_before(("CSE 216","C"; "CSE 260","C"), Sem),major("CSE"; "DAS").
course("CSE 306", 3).
has_prereq("CSE 306").
prereq("CSE 306", Sem) :- semester(Sem),passed_before(("CSE 320","C"; "ESE 280","C"), Sem),major("CSE"; "ECE").
course("CSE 307", 3).
has_prereq("CSE 307").
prereq("CSE 307", Sem) :- semester(Sem),passed_before(("CSE 214","C"), Sem),passed_before(("CSE 216","C"; "CSE 260","C"), Sem),major("CSE"; "DAS").
course("CSE 310", 3).
has_prereq("CSE 310").
prereq("CSE 310", Sem) :- semester(Sem),passed_before(("CSE 214","C"; "CSE 260","C"), Sem),passed_before(("CSE 220","C"; "ISE 218","C"), Sem),major("CSE"; "ISE").
course("CSE 311", 3).
has_prereq("CSE 311").
prereq("CSE 311", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 230"; "CSE 260"; "ISE 208"), Sem),major("ISE"; "CSE").
course("CSE 312", 3).
has_prereq("CSE 312").
prereq("CSE 312", Sem) :- semester(Sem),major("CSE"; "ISE"; "DAS"),standing("U3"; "U4"),unsupported_prereq.
course("CSE 316", 3).
has_prereq("CSE 316").
prereq("CSE 316", Sem) :- semester(Sem),passed_before(("CSE 214","C"; "CSE 260","C"), Sem),passed_before(("CSE 216","C"; "CSE 307","C"), Sem),major("CSE").
course("CSE 320", 3).
has_prereq("CSE 320").
prereq("CSE 320", Sem) :- semester(Sem),passed_before(("CSE 220","C"), Sem),major("CSE").
course("CSE 323", 3).
has_prereq("CSE 323").
prereq("CSE 323", Sem) :- semester(Sem), taken_before("CSE 214", Sem).
prereq("CSE 323", Sem) :- semester(Sem), taken_before("CSE 230", Sem).
prereq("CSE 323", Sem) :- semester(Sem), taken_before("CSE 260", Sem).
prereq("CSE 323", Sem) :- semester(Sem), taken_before("ISE 208", Sem).
course("CSE 325", 3).
has_prereq("CSE 325").
prereq("CSE 325", Sem) :- semester(Sem), taken_before("CSE 110", Sem).
prereq("CSE 325", Sem) :- semester(Sem), taken_before("CSE 101", Sem).
prereq("CSE 325", Sem) :- semester(Sem), taken_before("CSE 114", Sem).
course("CSE 327", 3).
has_prereq("CSE 327").
prereq("CSE 327", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 230"; "CSE 260"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem),major("CSE"; "ISE"; "DAS").
course("CSE 328", 3).
has_prereq("CSE 328").
prereq("CSE 328", Sem) :- semester(Sem),passed_before(("CSE 220","C"), Sem),major("CSE"; "DAS").
course("CSE 331", 3).
has_prereq("CSE 331").
prereq("CSE 331", Sem) :- semester(Sem),taken_before("CSE 220", Sem),major("CSE").
course("CSE 332", 3).
has_prereq("CSE 332").
prereq("CSE 332", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 260"), Sem),taken_before(("MAT 211"; "AMS 210"), Sem),taken_before(("AMS 110"; "AMS 310"), Sem),major("CSE"; "ISE"; "DAS").
course("CSE 333", 3).
has_prereq("CSE 333").
prereq("CSE 333", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
course("CSE 334", 3).
has_prereq("CSE 334").
prereq("CSE 334", Sem) :- semester(Sem),standing("U2"; "U3"; "U4"),major("CSE"; "ISE").
course("CSE 336", 3).
has_prereq("CSE 336").
prereq("CSE 336", Sem) :- semester(Sem),passed_before(("CSE 214","C"; "CSE 260","C"), Sem),major("CSE").
course("CSE 337", 3).
has_prereq("CSE 337").
prereq("CSE 337", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE"; "DAS"),standing("U3"; "U4").
course("CSE 350", 4).
has_prereq("CSE 350").
prereq("CSE 350", Sem) :- semester(Sem),taken_before(("CSE 113"; "CSE 150"; "CSE 215"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem),unsupported_prereq.
course("CSE 351", 3).
has_prereq("CSE 351").
prereq("CSE 351", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 260"), Sem),taken_before("AMS 310", Sem),major("CSE"; "DAS").
course("CSE 352", 3).
has_prereq("CSE 352").
prereq("CSE 352", Sem) :- semester(Sem),taken_before(("CSE 316"; "CSE 351"), Sem),major("CSE"; "DAS").
course("CSE 353", 3).
has_pre_or_coreq("CSE 353").
pre_or_coreq("CSE 353", Sem) :- semester(Sem), taken_before_or_same("AMS 310", Sem).
pre_or_coreq("CSE 353", Sem) :- semester(Sem), taken_before_or_same("AMS 311", Sem).
pre_or_coreq("CSE 353", Sem) :- semester(Sem), taken_before_or_same("AMS 412", Sem).
has_prereq("CSE 353").
prereq("CSE 353", Sem) :- semester(Sem),taken_before(("CSE 316"; "CSE 351"), Sem),major("CSE"; "DAS").
course("CSE 354", 3).
has_prereq("CSE 354").
prereq("CSE 354", Sem) :- semester(Sem),taken_before(("CSE 316"; "CSE 351"), Sem),major("CSE"; "DAS").
course("CSE 355", 3).
has_prereq("CSE 355").
prereq("CSE 355", Sem) :- semester(Sem),taken_before("AMS 301", Sem),unsupported_prereq.
course("CSE 356", 3).
has_prereq("CSE 356").
prereq("CSE 356", Sem) :- semester(Sem),passed_before(("CSE 316","C"), Sem),passed_before(("CSE 320","C"), Sem),major("CSE").
course("CSE 357", 3).
has_prereq("CSE 357").
prereq("CSE 357", Sem) :- semester(Sem),passed_before(("CSE 316","C"; "CSE 351","C"), Sem),passed_before(("AMS 310","C"), Sem),major("CSE"; "DAS").
course("CSE 360", 3).
has_prereq("CSE 360").
prereq("CSE 360", Sem) :- semester(Sem),taken_before("CSE 220", Sem),major("CSE").
course("CSE 361", 3).
has_prereq("CSE 361").
prereq("CSE 361", Sem) :- semester(Sem),taken_before("CSE 220", Sem),major("CSE").
course("CSE 362", 3).
has_prereq("CSE 362").
prereq("CSE 362", Sem) :- semester(Sem),taken_before("CSE 220", Sem),major("CSE").
course("CSE 363", 3).
has_prereq("CSE 363").
prereq("CSE 363", Sem) :- semester(Sem),taken_before("CSE 220", Sem),major("CSE").
course("CSE 364", 3).
has_prereq("CSE 364").
prereq("CSE 364", Sem) :- semester(Sem), taken_before("CSE 334", Sem).
prereq("CSE 364", Sem) :- semester(Sem), taken_before("ISE 334", Sem).
course("CSE 366", 3).
has_prereq("CSE 366").
prereq("CSE 366", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 260"), Sem),taken_before(("MAT 211"; "AMS 210"), Sem),major("CSE"; "ISE").
course("CSE 370", 3).
has_prereq("CSE 370").
prereq("CSE 370", Sem) :- semester(Sem),taken_before("CSE 310", Sem),major("CSE").
course("CSE 371", 3).
has_prereq("CSE 371").
prereq("CSE 371", Sem) :- semester(Sem), taken_before("CSE 113", Sem).
prereq("CSE 371", Sem) :- semester(Sem), taken_before("CSE 150", Sem).
prereq("CSE 371", Sem) :- semester(Sem), taken_before("CSE 215", Sem).
prereq("CSE 371", Sem) :- semester(Sem), taken_before("MAT 200", Sem).
prereq("CSE 371", Sem) :- semester(Sem), taken_before("MAT 250", Sem).
course("CSE 373", 3).
has_prereq("CSE 373").
prereq("CSE 373", Sem) :- semester(Sem),passed_before(("CSE 113","C"; "CSE 150","C"; "CSE 215","C"; "MAT 200","C"; "MAT 250","C"), Sem),passed_before(("MAT 211","C"; "AMS 210","C"), Sem),passed_before(("CSE 214","C"; "CSE 260","C"), Sem),major("CSE"; "MAT"; "DAS").
course("CSE 376", 3).
has_prereq("CSE 376").
prereq("CSE 376", Sem) :- semester(Sem),passed_before(("CSE 320","C"), Sem),major("CSE").
course("CSE 377", 3).
has_prereq("CSE 377").
prereq("CSE 377", Sem) :- semester(Sem),taken_before(("AMS 161"; "MAT 127"; "MAT 132"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem).
course("CSE 378", 3).
has_prereq("CSE 378").
prereq("CSE 378", Sem) :- semester(Sem),taken_before(("AMS 161"; "MAT 127"; "MAT 132"), Sem),taken_before(("AMS 210"; "MAT 211"; "MEC 262"), Sem).
course("CSE 380", 3).
has_prereq("CSE 380").
prereq("CSE 380", Sem) :- semester(Sem),taken_before("CSE 220", Sem),major("CSE").
course("CSE 381", 3).
has_prereq("CSE 381").
prereq("CSE 381", Sem) :- semester(Sem),taken_before("CSE 220", Sem),major("CSE").
course("CSE 385", 4).
has_prereq("CSE 385").
prereq("CSE 385", Sem) :- semester(Sem),taken_before(("CSE 113"; "CSE 150"; "CSE 215"; "MAT 200"; "MAT 250"), Sem),taken_before(("AMS 210"; "MAT 211"), Sem),taken_before(("CSE 214"; "CSE 260"), Sem),unsupported_prereq.
course("CSE 390", 3).
has_prereq("CSE 390").
prereq("CSE 390", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
course("CSE 391", 3).
has_prereq("CSE 391").
prereq("CSE 391", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
course("CSE 392", 3).
has_prereq("CSE 392").
prereq("CSE 392", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
course("CSE 393", 3).
has_prereq("CSE 393").
prereq("CSE 393", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
course("CSE 394", 3).
has_prereq("CSE 394").
prereq("CSE 394", Sem) :- semester(Sem),taken_before(("CSE 214"; "CSE 260"), Sem),major("CSE"; "ISE").
course("CSE 416", 3).
has_prereq("CSE 416").
prereq("CSE 416", Sem) :- semester(Sem),passed_before(("CSE 316","C"), Sem),standing("U4"),major("CSE").
course("CSE 475", 3).
has_prereq("CSE 475").
prereq("CSE 475", Sem) :- semester(Sem),unsupported_prereq,unsupported_prereq,unsupported_prereq.
course("CSE 487", 0).
course("CSE 487", 1).
course("CSE 487", 2).
course("CSE 487", 3).
has_prereq("CSE 487").
prereq("CSE 487", Sem) :- semester(Sem),permission.
course("CSE 488", 3).
has_prereq("CSE 488").
prereq("CSE 488", Sem) :- semester(Sem),major("CSE"),standing("U3"; "U4"),permission.
course("CSE 495", 3).
has_prereq("CSE 495").
prereq("CSE 495", Sem) :- semester(Sem),unsupported_prereq,permission.
course("CSE 496", 3).
has_prereq("CSE 496").
prereq("CSE 496", Sem) :- semester(Sem),taken_before("CSE 495", Sem),permission.
course("AMS 151", 3).
has_prereq("AMS 151").
prereq("AMS 151", Sem) :- semester(Sem), passed_before(("MAT 123","B"), Sem).
course("AMS 161", 3).
has_prereq("AMS 161").
prereq("AMS 161", Sem) :- semester(Sem), passed_before(("AMS 151","C"), Sem).
prereq("AMS 161", Sem) :- semester(Sem), passed_before(("MAT 131","C"), Sem).
course("AMS 210", 3).
has_prereq("AMS 210").
prereq("AMS 210", Sem) :- semester(Sem), taken_before("AMS 151", Sem).
prereq("AMS 210", Sem) :- semester(Sem), taken_before("MAT 131", Sem).
prereq("AMS 210", Sem) :- semester(Sem), taken_same("MAT 126").
course("AMS 301", 3).
has_prereq("AMS 301").
prereq("AMS 301", Sem) :- semester(Sem), taken_before("AMS 210", Sem).
prereq("AMS 301", Sem) :- semester(Sem), taken_before("MAT 211", Sem).
prereq("AMS 301", Sem) :- semester(Sem), taken_before("AMS 361", Sem).
prereq("AMS 301", Sem) :- semester(Sem), taken_before("MAT 303", Sem).
course("AMS 310", 3).
has_prereq("AMS 310").
prereq("AMS 310", Sem) :- semester(Sem), taken_before("AMS 161", Sem).
prereq("AMS 310", Sem) :- semester(Sem), taken_before("MAT 132", Sem).
prereq("AMS 310", Sem) :- semester(Sem), taken_before("MAT 127", Sem).
course("AMS 311", 3).
has_prereq("AMS 311").
prereq("AMS 311", Sem) :- semester(Sem), taken_before("AMS 301", Sem),taken_before("AMS 310", Sem).
prereq("AMS 311", Sem) :- semester(Sem), permission.
has_coreq("AMS 311").
coreq("AMS 311", Sem) :- semester(Sem), taken_same("MAT 203", Sem).
coreq("AMS 311", Sem) :- semester(Sem), taken_same("AMS 261", Sem).
course("MAT 123", 3).
has_prereq("MAT 123").
prereq("MAT 123", Sem) :- semester(Sem),unsupported_prereq.
course("MAT 125", 3).
has_prereq("MAT 125").
prereq("MAT 125", Sem) :- semester(Sem), passed_before(("MAT 123","C"), Sem).
prereq("MAT 125", Sem) :- semester(Sem), taken_same("MAT 130").
course("MAT 126", 3).
has_prereq("MAT 126").
prereq("MAT 126", Sem) :- semester(Sem), passed_before(("MAT 125","C"), Sem).
prereq("MAT 126", Sem) :- semester(Sem), passed_before(("MAT 131","C"), Sem).
prereq("MAT 126", Sem) :- semester(Sem), passed_before(("MAT 141","C"), Sem).
prereq("MAT 126", Sem) :- semester(Sem), passed_before(("AMS 151","C"), Sem).
course("MAT 127", 3).
has_prereq("MAT 127").
prereq("MAT 127", Sem) :- semester(Sem), passed_before(("MAT 126","C"), Sem).
course("MAT 131", 4).
has_prereq("MAT 131").
prereq("MAT 131", Sem) :- semester(Sem), passed_before(("MAT 123","B"), Sem).
course("MAT 132", 4).
has_prereq("MAT 132").
prereq("MAT 132", Sem) :- semester(Sem), passed_before(("AMS 151","C"), Sem).
prereq("MAT 132", Sem) :- semester(Sem), passed_before(("MAT 131","C"), Sem).
prereq("MAT 132", Sem) :- semester(Sem), passed_before(("MAT 141","C"), Sem).
course("MAT 211", 3).
has_prereq("MAT 211").
prereq("MAT 211", Sem) :- semester(Sem), passed_before(("AMS 151","C"), Sem).
prereq("MAT 211", Sem) :- semester(Sem), passed_before(("MAT 131","C"), Sem).
prereq("MAT 211", Sem) :- semester(Sem), passed_before(("MAT 141","C"), Sem).
prereq("MAT 211", Sem) :- semester(Sem), taken_same("MAT 126").
course("BIO 201", 3).
has_prereq("BIO 201").
prereq("BIO 201", Sem) :- semester(Sem),unsupported_prereq.
course("BIO 202", 3).
has_prereq("BIO 202").
prereq("BIO 202", Sem) :- semester(Sem), passed_before(("CHE 129","C"), Sem).
prereq("BIO 202", Sem) :- semester(Sem), passed_before(("CHE 131","C"), Sem).
prereq("BIO 202", Sem) :- semester(Sem), taken_same("CHE 152").
course("BIO 203", 3).
has_prereq("BIO 203").
prereq("BIO 203", Sem) :- semester(Sem), taken_before("CHE 129", Sem).
prereq("BIO 203", Sem) :- semester(Sem), taken_before("CHE 131", Sem).
prereq("BIO 203", Sem) :- semester(Sem), taken_same("CHE 152").
course("BIO 204", 2).
has_prereq("BIO 204").
prereq("BIO 204", Sem) :- semester(Sem), taken_before("CHE 129", Sem),taken_before("CHE 131", Sem).
prereq("BIO 204", Sem) :- semester(Sem), taken_same("CHE 152").
course("CHE 131", 4).
has_prereq("CHE 131").
prereq("CHE 131", Sem) :- semester(Sem),unsupported_prereq.
has_coreq("CHE 131").
coreq("CHE 131", Sem) :- semester(Sem),unsupported_coreq.
course("CHE 132", 4).
has_pre_or_coreq("CHE 132").
pre_or_coreq("CHE 132", Sem) :- semester(Sem),unsupported_pre_or_coreq,unsupported_pre_or_coreq.
has_prereq("CHE 132").
prereq("CHE 132", Sem) :- semester(Sem), passed_before(("CHE 129","C"), Sem).
prereq("CHE 132", Sem) :- semester(Sem), passed_before(("CHE 131","C"), Sem).
course("CHE 133", 1).
course("CHE 152", 4).
has_prereq("CHE 152").
prereq("CHE 152", Sem) :- semester(Sem),unsupported_prereq,unsupported_prereq.
course("CHE 154", 2).
has_coreq("CHE 154").
coreq("CHE 154", Sem) :- semester(Sem),taken_same("CHE 152", Sem).
course("CHE 321", 4).
has_prereq("CHE 321").
prereq("CHE 321", Sem) :- semester(Sem),passed_before(("CHE 132","C"), Sem).
course("CHE 322", 4).
has_prereq("CHE 322").
prereq("CHE 322", Sem) :- semester(Sem),passed_before(("CHE 321","C"), Sem).
course("CHE 331", 4).
has_prereq("CHE 331").
prereq("CHE 331", Sem) :- semester(Sem),passed_before(("CHE 152","C"), Sem).
has_coreq("CHE 331").
coreq("CHE 331", Sem) :- semester(Sem),taken_same("CHE 383", Sem).
course("CHE 332", 4).
has_prereq("CHE 332").
prereq("CHE 332", Sem) :- semester(Sem),passed_before(("CHE 331","C"), Sem).
course("PHY 125", 3).
has_prereq("PHY 125").
prereq("PHY 125", Sem) :- semester(Sem), taken_before("MAT 125", Sem).
course("PHY 126", 3).
has_prereq("PHY 126").
prereq("PHY 126", Sem) :- semester(Sem), passed_before(("PHY 125","C"), Sem).
prereq("PHY 126", Sem) :- semester(Sem), passed_before(("PHY 131","C"), Sem).
prereq("PHY 126", Sem) :- semester(Sem), passed_before(("PHY 141","C"), Sem).
course("PHY 127", 3).
has_prereq("PHY 127").
prereq("PHY 127", Sem) :- semester(Sem), passed_before(("PHY 125","C"), Sem).
prereq("PHY 127", Sem) :- semester(Sem), passed_before(("PHY 131","C"), Sem).
prereq("PHY 127", Sem) :- semester(Sem), passed_before(("PHY 141","C"), Sem).
course("PHY 131", 3).
has_prereq("PHY 131").
prereq("PHY 131", Sem) :- semester(Sem),unsupported_prereq.
course("PHY 132", 3).
has_prereq("PHY 132").
prereq("PHY 132", Sem) :- semester(Sem), passed_before(("PHY 131","C"), Sem).
prereq("PHY 132", Sem) :- semester(Sem), passed_before(("PHY 141","C"), Sem).
course("PHY 133", 1).
has_pre_or_coreq("PHY 133").
pre_or_coreq("PHY 133", Sem) :- semester(Sem),taken_before_or_same("PHY 125", Sem),taken_before_or_same("PHY 126", Sem),taken_before_or_same(("PHY 131"; "PHY 141"), Sem).
course("PHY 134", 1).
has_prereq("PHY 134").
prereq("PHY 134", Sem) :- semester(Sem),passed_before(("PHY 133","C"), Sem).
course("PHY 141", 3).
course("PHY 142", 3).
has_prereq("PHY 142").
prereq("PHY 142", Sem) :- semester(Sem), passed_before(("PHY 141","C"), Sem).
prereq("PHY 142", Sem) :- semester(Sem), permission.
course("PHY 251", 3).
has_pre_or_coreq("PHY 251").
pre_or_coreq("PHY 251", Sem) :- semester(Sem), taken_before_or_same("MAT 203", Sem).
pre_or_coreq("PHY 251", Sem) :- semester(Sem), taken_before_or_same("MAT 205", Sem).
pre_or_coreq("PHY 251", Sem) :- semester(Sem), taken_before_or_same("AMS 261", Sem).
pre_or_coreq("PHY 251", Sem) :- semester(Sem), taken_before_or_same("MAT 307", Sem).
has_prereq("PHY 251").
prereq("PHY 251", Sem) :- semester(Sem),aux_or_1(Sem),taken_before("PHY 134", Sem),passed_before(("MAT 126","C"; "MAT 132","C"; "MAT 142","C"; "MAT 171","C"; "AMS 161","C"), Sem).
course("PHY 252", 1).
has_pre_or_coreq("PHY 252").
pre_or_coreq("PHY 252", Sem) :- semester(Sem),taken_before_or_same("PHY 251", Sem).
course("GEO 102", 3).
course("GEO 103", 3).
course("GEO 112", 1).
course("GEO 122", 4).
course("AST 203", 4).
has_prereq("AST 203").
prereq("AST 203", Sem) :- semester(Sem), taken_before("PHY 125", Sem).
prereq("AST 203", Sem) :- semester(Sem), taken_before("PHY 133", Sem).
prereq("AST 203", Sem) :- semester(Sem), taken_before("PHY 131", Sem).
prereq("AST 203", Sem) :- semester(Sem), taken_before("PHY 141", Sem).
course("AST 205", 3).
has_prereq("AST 205").
prereq("AST 205", Sem) :- semester(Sem), taken_before("PHY 125", Sem).
prereq("AST 205", Sem) :- semester(Sem), taken_before("PHY 133", Sem).
prereq("AST 205", Sem) :- semester(Sem), taken_before("PHY 131", Sem).
prereq("AST 205", Sem) :- semester(Sem), taken_before("PHY 141", Sem).
course("WRT 101", 3).
has_prereq("WRT 101").
prereq("WRT 101", Sem) :- semester(Sem),unsupported_prereq.
course("WRT 102", 3).
has_prereq("WRT 102").
prereq("WRT 102", Sem) :- semester(Sem), passed_before(("WRT 101","C"), Sem).
course("AMS 110", 3).
has_prereq("AMS 110").
prereq("AMS 110", Sem) :- semester(Sem), taken_before("AMS 151", Sem).
prereq("AMS 110", Sem) :- semester(Sem), taken_before("MAT 125", Sem).
prereq("AMS 110", Sem) :- semester(Sem), taken_before("MAT 131", Sem).
has_anti_req("AMS 110").
anti_req("AMS 110", Sem) :- semester(Sem), taken_before("MAT 203", Sem).
anti_req("AMS 110", Sem) :- semester(Sem), taken_before("AMS 310", Sem).
course("AMS 261", 4).
has_prereq("AMS 261").
prereq("AMS 261", Sem) :- semester(Sem), taken_before("AMS 161", Sem).
prereq("AMS 261", Sem) :- semester(Sem), taken_before("MAT 127", Sem).
prereq("AMS 261", Sem) :- semester(Sem), taken_before("MAT 132", Sem).
course("AMS 361", 4).
has_prereq("AMS 361").
prereq("AMS 361", Sem) :- semester(Sem), taken_before("AMS 161", Sem).
prereq("AMS 361", Sem) :- semester(Sem), taken_before("MAT 127", Sem).
prereq("AMS 361", Sem) :- semester(Sem), taken_before("MAT 132", Sem).
course("AMS 412", 3).
has_prereq("AMS 412").
prereq("AMS 412", Sem) :- semester(Sem),taken_before("AMS 311", Sem).
course("MAT 130", 1).
has_prereq("MAT 130").
prereq("MAT 130", Sem) :- semester(Sem), taken_before("MAT 122", Sem).
prereq("MAT 130", Sem) :- semester(Sem), permission.
course("MAT 200", 3).
has_prereq("MAT 200").
prereq("MAT 200", Sem) :- semester(Sem),unsupported_prereq.
course("MAT 203", 4).
has_prereq("MAT 203").
prereq("MAT 203", Sem) :- semester(Sem), passed_before(("MAT 127","C"), Sem).
prereq("MAT 203", Sem) :- semester(Sem), passed_before(("MAT 132","C"), Sem).
prereq("MAT 203", Sem) :- semester(Sem), passed_before(("MAT 142","C"), Sem).
prereq("MAT 203", Sem) :- semester(Sem), passed_before(("AMS 161","C"), Sem).
course("MAT 250", 4).
has_prereq("MAT 250").
prereq("MAT 250", Sem) :- semester(Sem), taken_before("MAT 131", Sem).
course("MAT 303", 4).
has_prereq("MAT 303").
prereq("MAT 303", Sem) :- semester(Sem), passed_before(("MAT 127","C"), Sem).
prereq("MAT 303", Sem) :- semester(Sem), passed_before(("MAT 132","C"), Sem).
prereq("MAT 303", Sem) :- semester(Sem), passed_before(("MAT 142","C"), Sem).
prereq("MAT 303", Sem) :- semester(Sem), passed_before(("AMS 161","C"), Sem).
course("MAT 307", 4).
has_prereq("MAT 307").
prereq("MAT 307", Sem) :- semester(Sem), taken_before("MAT 127", Sem).
prereq("MAT 307", Sem) :- semester(Sem), taken_before("MAT 132", Sem).
course("CHE 129", 4).
has_prereq("CHE 129").
prereq("CHE 129", Sem) :- semester(Sem),unsupported_prereq.
has_coreq("CHE 129").
coreq("CHE 129", Sem) :- semester(Sem),taken_same("CHE 129", Sem),taken_same("MAT 123", Sem).
course("CHE 383", 2).
has_prereq("CHE 383").
prereq("CHE 383", Sem) :- semester(Sem),taken_before("CHE 154", Sem).
has_coreq("CHE 383").
coreq("CHE 383", Sem) :- semester(Sem),taken_same("CHE 331", Sem).
course("PHY 122", 4).
has_pre_or_coreq("PHY 122").
pre_or_coreq("PHY 122", Sem) :- semester(Sem), taken_before_or_same("CHE 132", Sem).
pre_or_coreq("PHY 122", Sem) :- semester(Sem), taken_before_or_same("CHE 152", Sem).
has_prereq("PHY 122").
prereq("PHY 122", Sem) :- semester(Sem),passed_before(("PHY 121","C"), Sem).
aux_or_1(Sem) :- semester(Sem), taken_before("PHY 122", Sem),taken_before("PHY 124", Sem).
aux_or_1(Sem) :- semester(Sem), taken_before("PHY 126", Sem),taken_before("PHY 127", Sem).
aux_or_1(Sem) :- semester(Sem), taken_before("PHY 132", Sem).
aux_or_1(Sem) :- semester(Sem), taken_before("PHY 142", Sem).