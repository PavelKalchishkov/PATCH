"""Bulgarian translations for PATCH, keyed by the English source text.

Run `python locale/fill_bg.py` after `manage.py makemessages -l bg` to copy these
into locale/bg/LC_MESSAGES/django.po, then `manage.py compilemessages`.
Plural entries map to a (one, many) tuple.
"""

BG = {
    # Accounts & roles
    "Email": "Имейл",
    "Full name": "Име и фамилия",
    "Phone (optional)": "Телефон (по желание)",
    "Citizen": "Гражданин",
    "Contractor": "Изпълнител",
    "Inspector": "Инспектор",
    "Administrator": "Администратор",
    "Inspector (needs admin approval)": "Инспектор (изисква одобрение от администратор)",
    "Role": "Роля",
    "Inspector accounts start as citizen accounts until an administrator approves them.":
        "Инспекторските профили започват като граждански, докато администратор не ги одобри.",
    "Company name (contractors)": "Име на фирма (за изпълнители)",
    "License number (contractors)": "Номер на лиценз (за изпълнители)",
    "Address (contractors)": "Адрес (за изпълнители)",
    "Company name is required for contractor accounts.": "Името на фирмата е задължително за профили на изпълнители.",
    "Company name": "Име на фирма",
    "License number": "Номер на лиценз",
    "Address": "Адрес",
    "Notes": "Бележки",
    "Name": "Име",
    "Another account already uses this email address.": "Друг профил вече използва този имейл адрес.",
    "Welcome to PATCH. Your inspector request was sent to an administrator. You can use PATCH as a citizen until it is approved.":
        "Добре дошли в PATCH. Заявката ви за инспектор е изпратена до администратор. Дотогава можете да използвате PATCH като гражданин.",
    "Welcome to PATCH.": "Добре дошли в PATCH.",
    "Account details updated.": "Данните на профила са обновени.",
    "Password changed.": "Паролата е сменена.",
    "Contractor profile updated.": "Профилът на изпълнителя е обновен.",
    "Approved: %(name)s is now %(role)s.": "Одобрено: %(name)s вече е с роля „%(role)s“.",
    "Declined %(name)s's request to become %(role)s.": "Заявката на %(name)s за роля „%(role)s“ е отказана.",
    "You cannot change your own role.": "Не можете да промените собствената си роля.",
    "%(name)s's role is now %(role)s.": "Ролята на %(name)s вече е „%(role)s“.",
    "You cannot block your own account.": "Не можете да блокирате собствения си профил.",
    "%(name)s was unblocked.": "%(name)s е отблокиран.",
    "%(name)s was blocked.": "%(name)s е блокиран.",

    # Statuses & choices
    "Reserved": "Резервирано",
    "In progress": "В процес",
    "Finished": "Завършено",
    "Reports": "Сигнали",
    "Open": "Отворени",
    "Repaired": "Ремонтиран",
    ("count", "Repaired"): "Ремонтирани",
    "Low": "Ниска",
    "Medium": "Средна",
    "High": "Висока",
    "Critical": "Критична",
    "Draft": "Чернова",
    "Assigned": "Възложена",
    "Accepted": "Приета",
    "Completed": "Завършена",
    "Approved": "Одобрена",
    "Rejected": "Отхвърлен",
    "Before": "Преди",
    "After": "След",
    "Other": "Друга",
    "Submitted": "Подаден",
    "Processing": "Обработва се",
    "Verified": "Потвърден",
    "Scheduled for repair": "Насрочен за ремонт",
    "Queued": "На опашка",
    "Running": "Изпълнява се",
    "Failed": "Неуспешна",

    # Flash messages
    "Priority override saved.": "Ръчният приоритет е запазен.",
    "Cost estimate generated.": "Количествено-стойностната сметка е генерирана.",
    "Someone else has already reserved this damage.": "Някой друг вече е резервирал тази повреда.",
    "Damage reserved. It is now in your repairs under Reserved.":
        "Повредата е резервирана. Ще я намерите в „Моите ремонти“ под „Резервирани“.",
    "Repair task created.": "Задачата за ремонт е създадена.",
    "This task is not assigned to you.": "Тази задача не е възложена на вас.",
    "Only reservations that have not started can be released.": "Могат да се освобождават само резервации, по които не е започната работа.",
    "Reservation released. The damage is available to other contractors again.":
        "Резервацията е освободена. Повредата отново е достъпна за други изпълнители.",
    "Work started.": "Работата е започната.",
    "Marked as finished. An inspector will review it.": "Отбелязано като завършено. Инспектор ще го прегледа.",
    "Unknown action.": "Непознато действие.",
    "This task can't do that from its current status.": "Това действие не е възможно при текущия статус на задачата.",
    "Only repairs the contractor has marked finished can be approved or sent back.":
        "Могат да се одобряват или връщат само ремонти, които изпълнителят е отбелязал като завършени.",
    "Add a note telling the contractor what to fix before sending the repair back.":
        "Добавете бележка какво трябва да поправи изпълнителят, преди да върнете ремонта.",
    "Photo attached.": "Снимката е прикачена.",
    "Contractor accounts don't file damage reports. Pick up verified damage from Available work.":
        "Изпълнителите не подават сигнали за повреди. Изберете потвърдена повреда от „Налична работа“.",
    "Report submitted. Computer vision analysis is running.": "Сигналът е подаден. Тече анализ с компютърно зрение.",
    "My reports": "Моите сигнали",
    "You can only view your own reports.": "Можете да преглеждате само собствените си сигнали.",
    "This report is already in the repair workflow and can no longer be deleted.":
        "Този сигнал вече е в процес на ремонт и не може да бъде изтрит.",
    "Report deleted.": "Сигналът е изтрит.",
    "Moderation flags saved.": "Маркировките са запазени.",

    # Report form
    "Device make": "Марка на устройството",
    "Capture angle": "Ъгъл на снимане",
    "Street or boulevard": "Улица или булевард",
    "District / municipality": "Район / община",

    # Layout & navigation
    "Road Inspector & Registry": "Инспектор и регистър на пътната настилка",
    "Public map": "Публична карта",
    "Damage register": "Регистър на повредите",
    "Available work": "Налична работа",
    "Report damage": "Подай сигнал",
    "Review": "Преглед",
    "Catalog": "Каталог",
    "Assign repair": "Възложи ремонт",
    "Vision jobs": "Задачи за анализ",
    "My repairs": "Моите ремонти",
    "Repairs": "Ремонти",
    "Users": "Потребители",
    "Inspector requests waiting": "Чакащи заявки за инспектор",
    "Sign in": "Вход",
    "Sign out": "Изход",
    "Register": "Регистрация",

    # Login / register / profile
    "Use the email address you registered with.": "Използвайте имейла, с който сте се регистрирали.",
    "Continue": "Продължи",
    "No account yet?": "Нямате профил?",
    "Create a PATCH account": "Създайте профил в PATCH",
    "Citizens report damage, contractors repair it. Inspector access has to be approved by an administrator.":
        "Гражданите подават сигнали, изпълнителите ремонтират. Достъпът на инспектор се одобрява от администратор.",
    "Profile": "Профил",
    "Active": "Активен",
    "Blocked": "Блокиран",
    "Member since %(date)s": "Член от %(date)s",
    "Your request for the %(requested)s role is waiting for an administrator. Until then you can use PATCH with the %(current)s role.":
        "Заявката ви за роля „%(requested)s“ чака одобрение от администратор. Дотогава използвате PATCH с роля „%(current)s“.",
    "Account details": "Данни на профила",
    "Your name and email are shown to inspectors on your reports. You sign in with your email.":
        "Името и имейлът ви се виждат от инспекторите в сигналите ви. Влизате с имейла си.",
    "Save changes": "Запази промените",
    "Change password": "Смяна на парола",
    "Enter your current password, then the new one twice.": "Въведете текущата си парола, след това новата два пъти.",
    "At least 8 characters, not too common and not entirely numeric.": "Поне 8 символа, да не е често срещана и да не е само от цифри.",
    "Update password": "Смени паролата",
    "Contractor profile": "Профил на изпълнител",
    "Company details shown to inspectors when they assign repair work.": "Данни за фирмата, които инспекторите виждат при възлагане на ремонти.",
    "Save company details": "Запази данните на фирмата",

    # Users admin
    "Inspector requests": "Заявки за инспектор",
    "These people asked for inspector access when they signed up. Inspectors can verify and reject reports, so only approve people you know. Until you decide, they use PATCH as citizens.":
        "Тези хора са поискали достъп на инспектор при регистрацията си. Инспекторите могат да потвърждават и отхвърлят сигнали, затова одобрявайте само хора, които познавате. Докато не решите, те използват PATCH като граждани.",
    "signed up %(date)s": "регистриран на %(date)s",
    "Decline": "Откажи",
    "Give %(name)s inspector access?": "Да се даде ли достъп на инспектор на %(name)s?",
    "Approve as %(role)s": "Одобри като %(role)s",
    "Accounts": "Профили",
    "Change roles, or block and unblock users. Blocked accounts cannot sign in. You can't change your own role or block yourself.":
        "Сменяйте роли или блокирайте и отблокирайте потребители. Блокираните профили не могат да влизат. Не можете да промените собствената си роля или да се блокирате.",
    "Status": "Статус",
    "Wants %(role)s": "Иска роля „%(role)s“",
    "you": "вие",
    "Role for %(name)s": "Роля на %(name)s",
    "Save": "Запази",
    "Block": "Блокирай",
    "Unblock": "Отблокирай",
    "Change this account to {role}?": "Да се смени ли ролята на този профил на „{role}“?",

    # Catalog
    "Damage catalog": "Каталог на повредите",
    "Code": "Код",
    "Unit": "Мярка",
    "Base price": "Базова цена",
    "Technique": "Технология",

    # Map
    "Public damage map": "Публична карта на повредите",
    "Non-rejected reports on the live register. Click a marker or a listing to inspect it. Faces and plates are blurred before annotated photos go public.":
        "Всички неотхвърлени сигнали в регистъра. Кликнете върху маркер или ред, за да го разгледате. Лицата и регистрационните номера се замъгляват, преди снимките да станат публични.",
    "Open damage": "Неремонтирана повреда",
    "Registered problems": "Регистрирани проблеми",
    "Click a pin on the map, or pick one below.": "Кликнете върху маркер на картата или изберете от списъка.",
    "Road report": "Сигнал за пътя",
    "Unnamed location": "Неозначено място",
    "Open this report": "Отвори сигнала",
    "See before & after": "Виж преди и след",
    "Selected problem": "Избран проблем",
    "No registered problems on the map yet.": "Все още няма регистрирани проблеми на картата.",

    # Register
    "Public damage register": "Публичен регистър на повредите",
    "Every damage on the live register. Repaired ones are shown in green; click them to see the road before and after the repair.":
        "Всички повреди в регистъра. Ремонтираните са в зелено – кликнете върху тях, за да видите пътя преди и след ремонта.",
    "Type": "Вид",
    "Street": "Улица",
    "Severity": "Тежест",
    "Priority": "Приоритет",
    "Cost": "Цена",
    "The register is empty.": "Регистърът е празен.",

    # Home
    "Home": "Начало",
    "Inspect, register and repair the road network.": "Проверявайте, регистрирайте и ремонтирайте пътната мрежа.",
    "Citizens report potholes and surface damage. Inspectors moderate the register. Contractors close the loop with photographed, approved repairs.":
        "Гражданите сигнализират за дупки и повреди по настилката. Инспекторите проверяват регистъра. Изпълнителите завършват цикъла с документирани и одобрени ремонти.",
    "Find available work": "Намери налична работа",
    "Review reports": "Прегледай сигнали",
    "Submit a road report": "Подай сигнал за пътя",
    "Open cases": "Отворени случаи",
    "For citizens": "За граждани",
    "Capture a photo, drop a GPS pin and track status from submission through repair.":
        "Направете снимка, отбележете мястото на картата и следете статуса от подаването до ремонта.",
    "For inspectors": "За инспектори",
    "Review spam and duplicates, confirm computer-vision detections, override priority and issue a BOQ.":
        "Отсейте спам и дублирани сигнали, потвърдете откритите повреди, задайте приоритет и изгответе КСС.",
    "For contractors": "За изпълнители",
    "Reserve verified damage, track it from reserved to in progress to finished, and upload before/after photos for municipal approval.":
        "Резервирайте потвърдени повреди, следете ги от резервация до завършване и качвайте снимки преди и след за одобрение от общината.",
    "Latest reports": "Последни сигнали",
    "District": "Район",
    "When": "Кога",
    "No reports yet. Be the first to file one.": "Все още няма сигнали. Бъдете първият, който ще подаде.",

    # Repair approval result
    "Repair approved": "Ремонтът е одобрен",
    "Repair sent back": "Ремонтът е върнат",
    "The linked reports are now marked repaired and the job is closed. They show in green on the public map.":
        "Свързаните сигнали са отбелязани като ремонтирани и задачата е приключена. Те се показват в зелено на публичната карта.",
    "It's back in the contractor's In progress list with your note. It will return to the Repairs tab once they mark it finished again.":
        "Ремонтът е върнат в списъка „В процес“ на изпълнителя заедно с бележката ви. Ще се появи отново в раздел „Ремонти“, когато го отбележи като завършен.",
    "Repair": "Ремонт",
    "New status": "Нов статус",
    "Sent back": "Върнат",
    "Note": "Бележка",
    "Reason": "Причина",
    "By": "От",
    "Review next repair": "Следващ ремонт",
    "Back to repairs": "Към ремонтите",
    "View this repair": "Виж ремонта",
    "%(counter)s repair still waiting for approval.": (
        "%(counter)s ремонт още чака одобрение.",
        "%(counter)s ремонта още чакат одобрение.",
    ),
    "No other repairs are waiting for approval.": "Няма други ремонти, които чакат одобрение.",

    # Available work & contractor board
    "Damage that inspectors have verified and nobody has reserved yet, most urgent first. Click a row to see the report, or reserve it straight away.":
        "Повреди, потвърдени от инспектор и още нерезервирани, подредени по спешност. Кликнете върху ред, за да видите сигнала, или го резервирайте директно.",
    "Damage": "Повреда",
    "Est. cost": "Ориент. цена",
    "Reserve": "Резервирай",
    "Nothing to pick up right now. New damage shows up here once an inspector verifies it.":
        "В момента няма налична работа. Новите повреди се появяват тук, след като инспектор ги потвърди.",
    "Work you've reserved or been assigned, from reservation to finished repair.":
        "Работа, която сте резервирали или ви е възложена – от резервацията до завършения ремонт.",
    "Find work": "Намери работа",
    "Task": "Задача",
    "Updated": "Обновена",
    "Awaiting approval": "Чака одобрение",
    'No reservations. Pick something up from <a href="%(available_url)s">Available work</a>.':
        'Няма резервации. Изберете нещо от <a href="%(available_url)s">Налична работа</a>.',
    "Nothing in progress. Start one of your reserved jobs.": "Няма ремонти в процес. Започнете някоя от резервираните задачи.",
    "No finished repairs yet.": "Все още няма завършени ремонти.",

    # Create repair
    "Create repair task": "Нова задача за ремонт",
    "Title": "Заглавие",
    "Description": "Описание",
    "Contractor team": "Екип на изпълнител",
    "Priority override": "Ръчен приоритет",
    "Confirmed damages": "Потвърдени повреди",
    "Verify detections on a report before assigning a repair.": "Потвърдете повредите в сигнала, преди да възложите ремонт.",
    "Assign": "Възложи",

    # Repair detail
    "Priority %(priority)s": "Приоритет %(priority)s",
    "Linked damages": "Свързани повреди",
    "Photos": "Снимки",
    "No site photos yet.": "Все още няма снимки от обекта.",
    "Kind": "Вид",
    "Photo": "Снимка",
    "Upload": "Качи",
    "Your progress": "Вашият напредък",
    'When your crew is on site, start the work. Add a "before" photo if you can.':
        "Когато екипът ви е на място, започнете работа. Ако можете, добавете снимка „преди“.",
    "Start work": "Започни работа",
    "Release this reservation? Other contractors will be able to take it.":
        "Да се освободи ли резервацията? Други изпълнители ще могат да я поемат.",
    "Release reservation": "Освободи резервацията",
    "An inspector sent this repair back. Check the task history for the reason, fix it, then mark it finished again.":
        "Инспектор е върнал този ремонт. Вижте причината в историята на задачата, отстранете проблема и отново го отбележете като завършен.",
    'Upload an "after" photo, then mark the repair finished for inspector approval.':
        "Качете снимка „след“ и отбележете ремонта като завършен, за да го одобри инспектор.",
    "Completion note (optional)": "Бележка при завършване (по желание)",
    "Mark finished": "Отбележи като завършен",
    "Approved by the municipality. Nice work.": "Одобрено от общината. Добра работа!",
    "Finished. Waiting for an inspector to approve the repair.": "Завършено. Чака одобрение от инспектор.",
    "Municipal approval": "Одобрение от общината",
    "The contractor marked this repair finished. Check the photos, then approve it or send it back.":
        "Изпълнителят е отбелязал ремонта като завършен. Проверете снимките и го одобрете или върнете.",
    "Note for the contractor": "Бележка за изпълнителя",
    "Required if you send it back": "Задължителна, ако го връщате",
    "Approve repair": "Одобри ремонта",
    "Send this repair back to the contractor?": "Да се върне ли ремонтът на изпълнителя?",
    "Send back": "Върни",
    "Approved. The linked reports are marked repaired.": "Одобрено. Свързаните сигнали са отбелязани като ремонтирани.",
    "Sent back to the contractor. It returns here once they mark it finished again.":
        "Върнато на изпълнителя. Ще се появи отново тук, когато го отбележи като завършен.",
    "Approval opens once the contractor marks the repair finished.": "Одобрението става възможно, след като изпълнителят отбележи ремонта като завършен.",
    "Task history": "История на задачата",
    "system": "системата",

    # Repair list
    "Repair tasks": "Задачи за ремонт",
    "Assign work": "Възложи работа",
    "Team": "Екип",
    "No repair tasks.": "Няма задачи за ремонт.",

    # Before / after
    "Repair confirmed by the municipality": "Ремонтът е потвърден от общината",
    "Repaired on %(date)s": "Ремонтиран на %(date)s",
    "Reported %(date)s": "Подаден на %(date)s",
    "The damage as reported": "Повредата при подаване на сигнала",
    "No photo was attached to the report.": "Към сигнала няма прикачена снимка.",
    "Now": "Сега",
    "Photographed %(date)s": "Заснето на %(date)s",
    "The road after the repair": "Пътят след ремонта",
    "The contractor didn't upload a photo of the finished repair.": "Изпълнителят не е качил снимка на завършения ремонт.",
    "Damage fixed": "Отстранена повреда",
    "Repaired by": "Ремонтирано от",
    "Method": "Технология",
    "Back to the map": "Към картата",
    "Full report": "Целият сигнал",

    # Report detail
    "Report": "Сигнал",
    "This damage has been repaired.": "Тази повреда е ремонтирана.",
    "See the before and after photos.": "Вижте снимките преди и след.",
    "Spam": "Спам",
    "Duplicate": "Дубликат",
    "Annotated damage": "Маркирана повреда",
    "Original capture": "Оригинална снимка",
    "Detections": "Открити повреди",
    "Confidence %(value)s": "Сигурност %(value)s",
    "Area %(value)s m2": "Площ %(value)s м²",
    "Depth %(value)s cm": "Дълбочина %(value)s см",
    "Suggested priority %(priority)s": "Предложен приоритет %(priority)s",
    "override %(priority)s": "ръчен %(priority)s",
    "Estimated cost": "Ориентировъчна цена",
    "Reserve this repair": "Резервирай ремонта",
    "In your repairs": "Във вашите ремонти",
    "Already taken by another contractor.": "Вече е поето от друг изпълнител.",
    "Manual priority override (1 = most urgent)": "Ръчен приоритет (1 = най-спешно)",
    "Save override": "Запази приоритета",
    "Generate BOQ / cost estimate": "Генерирай КСС / ценова оценка",
    "Item": "Позиция",
    "Qty": "Кол.",
    "Rate": "Ед. цена",
    "Total": "Общо",
    "No detections yet. The vision job may still be running.": "Все още няма открити повреди. Анализът може още да тече.",
    "Inspector review": "Проверка от инспектор",
    "Mark as spam": "Отбележи като спам",
    "Mark as duplicate": "Отбележи като дубликат",
    "Verify": "Потвърди",
    "Reject this report? It will be removed from the public map and register.":
        "Да се отхвърли ли сигналът? Ще бъде премахнат от публичната карта и регистъра.",
    "Reject": "Отхвърли",
    "Save flags": "Запази маркировките",
    "Delete report": "Изтрий сигнала",
    "Permanently removes this report, its photos and detections. This cannot be undone.":
        "Окончателно изтрива сигнала, снимките и откритите повреди. Действието е необратимо.",
    "Delete this report permanently?": "Да се изтрие ли сигналът окончателно?",
    "This report is already scheduled for repair or repaired, so it can no longer be deleted.":
        "Сигналът вече е насрочен за ремонт или е ремонтиран, затова не може да бъде изтрит.",
    "Status history": "История на статуса",
    "This report has already been reviewed.": "Този сигнал вече е прегледан.",
    "Rejected by %(name)s on %(date)s.": "Отхвърлен от %(name)s на %(date)s.",
    "Verified by %(name)s on %(date)s.": "Потвърден от %(name)s на %(date)s.",

    # My reports
    "Filed": "Подаден",
    "Delete": "Изтрий",
    "No reports yet.": "Все още няма сигнали.",

    # Review queue
    "Verify citizen damage reports, and approve repairs contractors have finished. Click a row to open it.":
        "Потвърждавайте сигнали от граждани и одобрявайте завършени от изпълнителите ремонти. Кликнете върху ред, за да го отворите.",
    "Damage reports": "Сигнали за повреди",
    "Confirm the detected damage, flag spam and duplicates, then verify or reject. The count shows reports still waiting for a decision.":
        "Проверете откритите повреди, отбележете спам и дубликати, след това потвърдете или отхвърлете. Броят показва сигналите, които още чакат решение.",
    "Citizen": "Гражданин",
    "Flags": "Маркировки",
    "No reports to review.": "Няма сигнали за преглед.",
    "Contractors marked these repairs finished. Check the photos, then approve them or send them back. Oldest first.":
        "Изпълнителите са отбелязали тези ремонти като завършени. Проверете снимките и ги одобрете или върнете. Най-старите са първи.",
    "Contractor": "Изпълнител",
    "No finished repairs waiting for approval.": "Няма завършени ремонти, които чакат одобрение.",

    # Report review result
    "Report verified": "Сигналът е потвърден",
    "Report rejected": "Сигналът е отхвърлен",
    "%(counter)s damage confirmed and added to the public register. Contractors can now reserve the repair work.": (
        "%(counter)s повреда е потвърдена и добавена в публичния регистър. Изпълнителите вече могат да резервират ремонта.",
        "%(counter)s повреди са потвърдени и добавени в публичния регистър. Изпълнителите вече могат да резервират ремонта.",
    ),
    "The report is on the public register. No damage was detected on it, so there is nothing for contractors to reserve.":
        "Сигналът е в публичния регистър. В него не са открити повреди, затова няма какво да резервират изпълнителите.",
    "It has been removed from the public map and register. The citizen who filed it can still see it, marked as rejected.":
        "Сигналът е премахнат от публичната карта и регистъра. Гражданинът, който го е подал, все още го вижда като отхвърлен.",
    "Damages": "Повреди",
    "Review next report": "Следващ сигнал",
    "Back to review queue": "Към списъка за преглед",
    "View this report": "Виж сигнала",
    "%(counter)s report still waiting for review.": (
        "%(counter)s сигнал още чака преглед.",
        "%(counter)s сигнала още чакат преглед.",
    ),
    "The review queue is clear. Nothing else is waiting.": "Няма чакащи сигнали за преглед.",

    # Submit
    "Submit report": "Подай сигнал",
    "Report road damage": "Сигнал за повреда на пътя",
    "Click the map to set the GPS point (WGS 84). The original photo is stored as a file URL, then sent to the vision pipeline.":
        "Кликнете върху картата, за да отбележите GPS точката (WGS 84). Снимката се запазва и се изпраща за анализ с компютърно зрение.",
    "No point selected yet.": "Все още няма избрана точка.",
    "Submit and analyse": "Изпрати за анализ",
    "Point": "Точка",

    # Vision jobs
    "Computer vision pipeline": "Анализ с компютърно зрение",
    "Background jobs call the model, write detections, and blur faces and plates before annotated images go public.":
        "Фонови задачи пускат модела, записват откритите повреди и замъгляват лица и номера, преди снимките да станат публични.",
    "Job": "Задача",
    "Log": "Журнал",
    "No jobs have been queued.": "Няма задачи на опашката.",
    "unlocated": "без местоположение",
    "Report %(id)s · %(place)s": "Сигнал %(id)s · %(place)s",
    # Error screens
    "Error %(code)s": "Грешка %(code)s",
    "Try again": "Опитай отново",
    "Go to the home page": "Към началната страница",
    "Go back": "Назад",
    "Something was wrong with that request": "Нещо в заявката не е наред",
    "The page couldn't understand what was sent. Go back and try again.": "Страницата не успя да обработи изпратеното. Върнете се и опитайте отново.",
    "You don't have access to this page": "Нямате достъп до тази страница",
    "Your account's role can't open this section. If you think it should, ask an administrator.":
        "Ролята на профила ви няма достъп до този раздел. Ако смятате, че трябва да има, обърнете се към администратор.",
    "Page not found": "Страницата не е намерена",
    "The page or report you're looking for doesn't exist. It may have been deleted, or the link is wrong.":
        "Страницата или сигналът, който търсите, не съществува. Може да е изтрит или връзката да е грешна.",
    "Something went wrong on our side": "Възникна грешка от наша страна",
    "The action didn't go through and nothing was changed. Please try again in a moment.":
        "Действието не беше изпълнено и нищо не е променено. Моля, опитайте отново след малко.",
    "Your form expired": "Формулярът е изтекъл",
    "For your security, forms expire after a while or when you sign in somewhere else. Nothing was saved. Reload the page and submit it again.":
        "За ваша сигурност формулярите изтичат след известно време или при вход от друго място. Нищо не е запазено. Презаредете страницата и изпратете отново.",
    "Reload the form": "Презареди формуляра",

    # Failed report submission
    "Your report wasn't submitted": "Сигналът ви не беше изпратен",
    "Something went wrong while saving it, so nothing was sent. Please try again. You'll need to choose the photo and the point on the map again.":
        "Възникна грешка при запазването, затова нищо не е изпратено. Моля, опитайте отново – ще трябва да изберете снимката и точката на картата наново.",
    "Your report was saved, but the automatic photo analysis couldn't start. An inspector will review it manually.":
        "Сигналът ви е запазен, но автоматичният анализ на снимката не успя да стартира. Инспектор ще го прегледа ръчно.",
    "Add a photo of the damage.": "Добавете снимка на повредата.",
    "That file isn't a photo we can read. Upload a JPG or PNG image.": "Файлът не е снимка, която можем да прочетем. Качете изображение в JPG или PNG формат.",
    "Choose the location by clicking the map.": "Изберете мястото, като кликнете върху картата.",
    "Your report wasn't submitted.": "Сигналът ви не беше изпратен.",
    "Fix the following and send it again:": "Поправете следното и изпратете отново:",
    "For your security, the browser clears the chosen photo after a failed attempt, so please add it again.":
        "От съображения за сигурност браузърът изчиства избраната снимка след неуспешен опит, затова я добавете отново.",
    "Sending…": "Изпращане…",

    # Map filters
    "Show on the map": "Покажи на картата",
    "All": "Всички",
    "Not fixed": "Неремонтирани",
    "Fixed": "Ремонтирани",
    "Awaiting review": "Чакат преглед",
    "Reports no inspector has verified or rejected yet": "Сигнали, които още не са потвърдени или отхвърлени от инспектор",
    "The map data couldn't be loaded.": "Данните за картата не можаха да се заредят.",
    "Check your connection and try again.": "Проверете връзката си и опитайте отново.",
    "Review this report": "Прегледай сигнала",
    "No unfixed road problems right now.": "В момента няма неремонтирани проблеми.",
    "No repaired road problems yet.": "Все още няма ремонтирани проблеми.",
    "Nothing is waiting for review. Every report has been verified or rejected.": "Няма сигнали за преглед. Всички са потвърдени или отхвърлени.",
    # Address autofill
    "Looking up the street…": "Търсене на улицата…",
    "Filled in from the map point. You can change it.": "Попълнено според точката на картата. Можете да го промените.",
    "No street name was found at this point. Please type it in.": "Не е намерена улица в тази точка. Моля, въведете я.",
    "The street couldn't be looked up right now. Please type it in.": "Улицата не можа да бъде намерена в момента. Моля, въведете я.",
    # Camera report
    "Take a photo of the damage with the camera.": "Снимайте повредата с камерата.",
    "The photo couldn't be read. Please take it again.": "Снимката не можа да бъде прочетена. Моля, снимайте отново.",
    "Your location wasn't captured. Allow location access and take the photo again.":
        "Местоположението ви не беше определено. Разрешете достъп до местоположението и снимайте отново.",
    "Take the photo with the camera on this page, then send the report.": "Снимайте с камерата на тази страница и след това изпратете сигнала.",
    "The photo is too old. Take a new photo and send the report right away.": "Снимката е твърде стара. Направете нова снимка и изпратете сигнала веднага.",
    "Point the camera at the damage and take a photo. Your location is added automatically from where you take it.":
        "Насочете камерата към повредата и снимайте. Местоположението ви се добавя автоматично от мястото на снимката.",
    "Please take the photo again; it isn't kept after a failed attempt.": "Моля, снимайте отново – снимката не се запазва след неуспешен опит.",
    "The photo you took": "Направената снимка",
    "Starting the camera…": "Включване на камерата…",
    "Switch camera": "Смени камерата",
    "Take photo": "Снимай",
    "Retake photo": "Снимай отново",
    "Getting your location…": "Определяне на местоположението…",
    "The pin shows where the photo was taken. It can't be moved by hand.": "Маркерът показва къде е направена снимката. Не може да се мести ръчно.",
    "The camera and location only work over a secure connection (HTTPS). Open PATCH through its https:// address.":
        "Камерата и местоположението работят само през защитена връзка (HTTPS). Отворете PATCH през адреса му с https://.",
    "This browser can't use the camera. Try a current version of Chrome, Safari, Firefox or Edge.":
        "Този браузър не може да използва камерата. Опитайте с актуална версия на Chrome, Safari, Firefox или Edge.",
    "Camera access is blocked. Allow the camera for this site in your browser settings, then reload the page.":
        "Достъпът до камерата е блокиран. Разрешете камерата за този сайт в настройките на браузъра и презаредете страницата.",
    "No camera was found on this device.": "На това устройство не е открита камера.",
    "The camera is being used by another app. Close it and reload the page.": "Камерата се използва от друго приложение. Затворете го и презаредете страницата.",
    "The camera couldn't be started. Reload the page to try again.": "Камерата не можа да се включи. Презаредете страницата, за да опитате отново.",
    "Location found (± {m} m).": "Местоположението е намерено (± {m} м).",
    "Photo taken here (± {m} m).": "Снимката е направена тук (± {m} м).",
    "Photo taken. Waiting for your location…": "Снимката е направена. Изчакване на местоположението…",
    "Location access is blocked. Allow location for this site in your browser settings, then reload the page.":
        "Достъпът до местоположението е блокиран. Разрешете го за този сайт в настройките на браузъра и презаредете страницата.",
    "Your location couldn't be found. Turn on location services, step outside if you can, and retake the photo.":
        "Местоположението ви не можа да бъде определено. Включете услугите за местоположение, излезте навън, ако можете, и снимайте отново.",
    "Filled in from where you took the photo. You can change it.": "Попълнено според мястото на снимката. Можете да го промените.",
    # One repair per report
    "Someone else has already reserved this repair.": "Някой друг вече е резервирал този ремонт.",
    "Repair reserved. It is now in your repairs under Reserved.": "Ремонтът е резервиран. Ще го намерите в „Моите ремонти“ под „Резервирано“.",
    "Choose the report to repair.": "Изберете сигнала за ремонт.",
    "Choose the contractor team that will do the repair.": "Изберете екипа на изпълнителя, който ще извърши ремонта.",
    "That report is no longer available. It may have been reserved by a contractor.": "Сигналът вече не е наличен. Може да е резервиран от изпълнител.",
    "Everything found in this report is repaired as one job.": "Всичко, открито в този сигнал, се ремонтира като една задача.",
    "Repair status": "Статус на ремонта",
    "Open in your repairs": "Отвори в „Моите ремонти“",
    "Open the repair task": "Отвори задачата за ремонт",
    "Reports that inspectors have verified and nobody has reserved yet, most urgent first. Each report is one repair, including every damage found in it. Click a row to see the report, or reserve it straight away.":
        "Сигнали, потвърдени от инспектор и още нерезервирани, подредени по спешност. Всеки сигнал е един ремонт, включващ всички открити в него повреди. Кликнете върху ред, за да видите сигнала, или го резервирайте директно.",
    "Every report on the live register, one repair each. Repaired ones are shown in green; click them to see the road before and after the repair.":
        "Всички сигнали в регистъра – по един ремонт на сигнал. Ремонтираните са в зелено – кликнете върху тях, за да видите пътя преди и след ремонта.",
    "Pick one verified report and the team that will repair it. The task covers every damage found in the report.":
        "Изберете един потвърден сигнал и екипа, който ще го ремонтира. Задачата обхваща всички открити в сигнала повреди.",
    "The repair wasn't assigned.": "Ремонтът не беше възложен.",
    "No verified reports are waiting for a repair. Verify a report first.": "Няма потвърдени сигнали, които чакат ремонт. Първо потвърдете сигнал.",
    "Title (optional)": "Заглавие (по желание)",
    "Filled in from the report if left empty": "Попълва се от сигнала, ако е празно",
    "Description (optional)": "Описание (по желание)",
    # Spam protection
    "%(name)s's spam strikes were reset. They can report again.": "Нарушенията за спам на %(name)s са нулирани. Отново може да подава сигнали.",
    "You've reached the limit of %(hour)s reports an hour and %(day)s a day. You can send the next one at %(time)s.":
        "Достигнахте ограничението от %(hour)s сигнала на час и %(day)s на ден. Следващия можете да изпратите в %(time)s.",
    "Your account can no longer send reports because %(limit)s of your reports were marked as spam. If you think this is a mistake, contact an administrator.":
        "Профилът ви вече не може да подава сигнали, защото %(limit)s от сигналите ви са отбелязани като спам. Ако смятате, че това е грешка, свържете се с администратор.",
    "This problem may already be reported nearby. Take the photo again and choose whether it's the same problem.":
        "Възможно е проблемът вече да е подаден наблизо. Снимайте отново и изберете дали е същият проблем.",
    "Something went wrong while saving it, so nothing was sent. Please take the photo again and resend it.":
        "Възникна грешка при запазването, затова нищо не е изпратено. Моля, снимайте отново и изпратете пак.",
    "You already reported this problem.": "Вече сте подали сигнал за този проблем.",
    "This report is already closed, so it can't take more photos.": "Сигналът вече е приключен и не приема повече снимки.",
    "You've already added a photo to this report.": "Вече сте добавили снимка към този сигнал.",
    "Your photo was taken too far from this report to confirm it.": "Снимката ви е направена твърде далеч от този сигнал, за да го потвърди.",
    "Thank you. Your photo was added to the existing report, which helps inspectors prioritise it.":
        "Благодарим ви! Снимката ви е добавена към съществуващия сигнал, което помага на инспекторите да определят приоритета му.",
    "Spam strikes": "Нарушения (спам)",
    "Can't report": "Без право на сигнали",
    "Reset this person's spam strikes? They'll be able to report again.": "Да се нулират ли нарушенията за спам? Потребителят отново ще може да подава сигнали.",
    "Reset": "Нулирай",
    "Also reported by %(counter)s more person": (
        "Подаден и от още %(counter)s човек",
        "Подаден и от още %(counter)s души",
    ),
    "Their photos were taken within a few metres of this report. Only inspectors and administrators see them.":
        "Снимките им са направени на няколко метра от този сигнал. Виждат ги само инспектори и администратори.",
    "Confirmation photo": "Снимка – потвърждение",
    "+%(counter)s photo": ("+%(counter)s снимка", "+%(counter)s снимки"),
    "Reporting is switched off for your account": "Подаването на сигнали е спряно за профила ви",
    "You've sent the maximum number of reports for now": "Изпратихте максималния брой сигнали засега",
    "See my reports": "Виж моите сигнали",
    "You can send %(hour)s more of %(max_hour)s reports this hour and %(day)s more of %(max_day)s today.":
        "Можете да изпратите още %(hour)s от %(max_hour)s сигнала този час и още %(day)s от %(max_day)s днес.",
    "Is this the same problem?": "Същият проблем ли е?",
    "Someone already reported a problem right here. If it's the same one, add your photo to it instead of sending a new report.":
        "Някой вече е подал сигнал точно тук. Ако е същият проблем, добавете снимката си към него, вместо да изпращате нов сигнал.",
    "No, it's a different problem": "Не, друг проблем е",
    "Yes, add my photo to this report": "Да, добави снимката ми към този сигнал",
    "You reported this one yourself.": "Вие сте подали този сигнал.",
    "You already added a photo to this one.": "Вече сте добавили снимка към него.",
    "{m} m away": "на {m} м",
    "Choose whether this is the same problem as the report shown above.": "Изберете дали това е същият проблем като показания по-горе сигнал.",
    # Finishing a repair
    "That file isn't a photo we can read. Take or choose the photo again.": "Файлът не е снимка, която можем да прочетем. Снимайте или изберете снимката отново.",
    "Add a photo of the finished repair before marking it finished.": "Добавете снимка на завършения ремонт, преди да го отбележите като завършен.",
    "When the work is done, add a photo of the finished repair and mark it finished for inspector approval.":
        "Когато работата е готова, добавете снимка на завършения ремонт и го отбележете като завършен за одобрение от инспектор.",
    "Photo of the finished repair": "Снимка на завършения ремонт",
    "Photo of the finished repair (required)": "Снимка на завършения ремонт (задължителна)",
    "Your photo of the finished repair": "Вашата снимка на завършения ремонт",
    'Your "after" photo from %(date)s will be used. Add a new one only if you want to replace it.':
        "Ще се използва снимката ви „след“ от %(date)s. Добавете нова само ако искате да я замените.",
    # Contractor map filters
    "Verified reports nobody has reserved yet": "Потвърдени сигнали, които още никой не е резервирал",
    "Available to reserve": "За резервиране",
    "View and reserve": "Виж и резервирай",
    "An inspector hasn't checked this report yet, so it can't be reserved.": "Инспектор още не е проверил този сигнал, затова не може да бъде резервиран.",
    "Another contractor is already repairing this.": "Друг изпълнител вече ремонтира това.",
    "Nothing is available to reserve right now. New work appears here once an inspector verifies a report.":
        "В момента няма нищо за резервиране. Новата работа се появява тук, след като инспектор потвърди сигнал.",
    # Map categories
    "Checked by an inspector, not repaired yet": "Проверени от инспектор, още неремонтирани",
    # Photo quality, votes, no-damage message, send-back reason
    "Accurate": "Точен",
    "The photo is too small. Take it with the camera on this page.": "Снимката е твърде малка. Снимайте с камерата на тази страница.",
    "The photo is too dark. Make sure nothing covers the camera and there is enough light, then take it again.":
        "Снимката е твърде тъмна. Уверете се, че нищо не закрива камерата и има достатъчно светлина, и снимайте отново.",
    "The photo is almost white. Don't point the camera at the sun or a bright light, then take it again.":
        "Снимката е почти бяла. Не насочвайте камерата към слънцето или силна светлина и снимайте отново.",
    "The photo looks blank, with no detail. Point the camera at the road damage and take it again.":
        "Снимката изглежда празна, без детайли. Насочете камерата към повредата на пътя и снимайте отново.",
    "The photo is too blurry. Hold the phone still for a moment and take it again.":
        "Снимката е твърде размазана. Задръжте телефона неподвижно за момент и снимайте отново.",
    "You can't vote on this report.": "Не можете да гласувате за този сигнал.",
    "Your vote was removed.": "Гласът ви е премахнат.",
    "Thank you. Inspectors will see that you flagged this report as spam.": "Благодарим ви! Инспекторите ще видят, че сте отбелязали сигнала като спам.",
    "Thank you for confirming this report is accurate.": "Благодарим ви, че потвърдихте, че сигналът е точен.",
    "{n} confirmed accurate": "{n} потвърдиха, че е точен",
    "An inspector sent this repair back.": "Инспектор върна този ремонт.",
    "Reason: %(reason)s": "Причина: %(reason)s",
    "Fix it, then add a new photo and mark it finished again.": "Поправете го, добавете нова снимка и отново го отбележете като завършен.",
    "Is this report accurate?": "Точен ли е този сигнал?",
    "%(counter)s person confirmed it's accurate.": (
        "%(counter)s човек потвърди, че е точен.",
        "%(counter)s души потвърдиха, че е точен.",
    ),
    "Flagged as spam by %(counter)s person": (
        "Отбелязан като спам от %(counter)s човек",
        "Отбелязан като спам от %(counter)s души",
    ),
    "You confirmed it's accurate": "Потвърдихте, че е точен",
    "It's accurate": "Точен е",
    "Report this as spam? Inspectors will review it.": "Да се отбележи ли като спам? Инспекторите ще го прегледат.",
    "You reported it as spam (undo)": "Отбелязахте го като спам (отмени)",
    "Report as spam": "Отбележи като спам",
    "Other citizens can confirm your report or flag it.": "Другите граждани могат да потвърдят сигнала ви или да го отбележат.",
    "to confirm this report or flag it as spam.": "за да потвърдите сигнала или да го отбележите като спам.",
    "No road damage was found in this photo.": "В тази снимка не е открита повреда на пътя.",
    "If the damage is clearly visible, an inspector will still check the report. Otherwise, take a closer, clearer photo and report it again.":
        "Ако повредата се вижда ясно, инспектор все пак ще провери сигнала. Иначе направете по-близка и ясна снимка и подайте сигнала отново.",
    "The photo couldn't be analysed automatically. An inspector will check it by hand.": "Снимката не можа да бъде анализирана автоматично. Инспектор ще я провери ръчно.",
    "The photo is still being analysed. Refresh the page in a moment.": "Снимката все още се анализира. Презаредете страницата след малко.",
    "%(counter)s spam flag": ("%(counter)s сигнал за спам", "%(counter)s сигнала за спам"),
    # Email verification
    "Confirm your email address for PATCH": "Потвърдете имейл адреса си в PATCH",
    "We sent a link to %(email)s. Open it to verify your email address.": "Изпратихме връзка на %(email)s. Отворете я, за да потвърдите имейл адреса си.",
    "Your email changed, so it needs verifying again. We sent a link to %(email)s.": "Имейлът ви е променен и трябва да бъде потвърден отново. Изпратихме връзка на %(email)s.",
    "This verification link doesn't work": "Тази връзка за потвърждение не работи",
    "It may have expired, been used for an old email address, or been copied incompletely. Sign in and send yourself a new link from your profile.":
        "Може да е изтекла, да е за стар имейл адрес или да е копирана непълно. Влезте и си изпратете нова връзка от профила.",
    "Go to my profile": "Към профила ми",
    "Your email address was already verified.": "Имейл адресът ви вече е потвърден.",
    "Thank you. Your email address %(email)s is verified.": "Благодарим ви! Имейл адресът ви %(email)s е потвърден.",
    "We sent a new link to %(email)s. Check your inbox and spam folder.": "Изпратихме нова връзка на %(email)s. Проверете входящата поща и папката за спам.",
    "A link was sent less than two minutes ago. Please check your inbox first.": "Преди по-малко от две минути беше изпратена връзка. Моля, първо проверете пощата си.",
    "Hello %(name)s,": "Здравейте, %(name)s,",
    "Please confirm that this is your email address for PATCH by opening this link:": "Моля, потвърдете, че това е вашият имейл адрес в PATCH, като отворите тази връзка:",
    "The link works for %(counter)s day.": ("Връзката е валидна %(counter)s ден.", "Връзката е валидна %(counter)s дни."),
    "If you didn't create a PATCH account, you can ignore this email.": "Ако не сте създавали профил в PATCH, можете да пренебрегнете този имейл.",
    "Your email address is confirmed": "Имейл адресът ви е потвърден",
    "Email verified": "Потвърден имейл",
    "Email not verified": "Непотвърден имейл",
    "Your email address is verified": "Имейл адресът ви е потвърден",
    "%(email)s, confirmed on %(date)s. Your reports show as coming from a verified account.":
        "%(email)s, потвърден на %(date)s. Сигналите ви се показват като подадени от потвърден профил.",
    "Your email address isn't verified yet": "Имейл адресът ви още не е потвърден",
    "Open the link we sent to %(email)s. Reports from verified accounts are easier for inspectors to trust.":
        "Отворете връзката, която изпратихме на %(email)s. На сигналите от потвърдени профили инспекторите се доверяват по-лесно.",
    "Send verification email": "Изпрати имейл за потвърждение",
    "The person who sent this report has confirmed their email address": "Подателят на сигнала е потвърдил имейл адреса си",
    "Verified account": "Потвърден профил",
    "The person who sent this report hasn't confirmed their email address": "Подателят на сигнала не е потвърдил имейл адреса си",
    "Unverified account": "Непотвърден профил",
    # Honest email sending messages
    "Your email changed, so it needs verifying again.": "Имейлът ви е променен и трябва да бъде потвърден отново.",
    "We sent a link to %(email)s. Check your inbox and spam folder.": "Изпратихме връзка на %(email)s. Проверете входящата поща и папката за спам.",
    "Email sending isn't set up on this server, so no email was sent. Use the verification link on your profile page.":
        "Изпращането на имейли не е настроено на този сървър, затова не е изпратен имейл. Използвайте връзката за потвърждение в профила си.",
    "The verification email couldn't be sent right now. Try again from your profile in a few minutes.":
        "Имейлът за потвърждение не можа да бъде изпратен в момента. Опитайте отново от профила си след няколко минути.",
    "Email sending isn't set up on this server, so use this link instead:": "Изпращането на имейли не е настроено на този сървър, затова използвайте тази връзка:",
    "Verify my email now": "Потвърди имейла ми сега",
}
