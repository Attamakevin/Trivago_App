function safeGetElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.warn(`Element with id '${id}' not found`);
    }
    return element;
}

function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    const backdrop = document.getElementById('mobileMenuBackdrop');
    const menuTrigger = document.querySelector('.menu-trigger');

    if (mobileMenu.classList.contains('hidden')) {
        // Show menu
        mobileMenu.classList.remove('hidden');
        mobileMenu.classList.add('active');
        backdrop.classList.add('active');
        menuTrigger.classList.add('active');

        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    } else {
        // Hide menu
        mobileMenu.classList.remove('active');
        mobileMenu.classList.add('hidden');
        backdrop.classList.remove('active');
        menuTrigger.classList.remove('active');

        // Restore body scroll
        document.body.style.overflow = 'auto';
    }
}

// Close mobile menu when clicking outside or on backdrop
document.addEventListener('click', function (event) {
    const mobileMenu = document.getElementById('mobileMenu');
    const menuTrigger = document.querySelector('.menu-trigger');
    const backdrop = document.getElementById('mobileMenuBackdrop');

    // Close if clicked on backdrop
    if (event.target === backdrop) {
        toggleMobileMenu();
    }

    // Close if clicked outside menu and trigger
    if (!mobileMenu.contains(event.target) &&
        !menuTrigger.contains(event.target) &&
        !mobileMenu.classList.contains('hidden')) {
        toggleMobileMenu();
    }
});

// Close mobile menu when window is resized to desktop
window.addEventListener('resize', function () {
    if (window.innerWidth > 768) {
        const mobileMenu = document.getElementById('mobileMenu');
        const backdrop = document.getElementById('mobileMenuBackdrop');

        mobileMenu.classList.remove('active');
        mobileMenu.classList.add('hidden');
        backdrop.classList.remove('active');
        document.querySelector('.menu-trigger').classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});

// Google translator
// function googleTranslateElementInit() {
//     new google.translate.TranslateElement(
//         { pageLanguage: 'en' },
//         'google_translate_element'
//     );
// }


// Booking Search Function

let guestCounts = {
    adults: 2,
    children: 0,
    rooms: 1
};

// Calendar state
let currentMonthIndex = 5; // June 2025 (0-based)
let currentYear = 2025;
let currentMonthIndexCheckout = 5; // For checkout calendar
let currentYearCheckout = 2025;

const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
];

// Initialize calendars when page loads
document.addEventListener('DOMContentLoaded', function () {
    updateCalendarDisplay('checkin');
    updateCalendarDisplay('checkout');
});

function toggleDropdown(type) {
    // Close all dropdowns first
    const dropdowns = ['locationDropdown', 'checkinDropdown', 'checkoutDropdown', 'guestsDropdown'];
    dropdowns.forEach(id => {
        const dropdown = document.getElementById(id);
        if (dropdown && !dropdown.id.includes(type)) {
            dropdown.classList.remove('dropdown-active');
        }
    });

    // Toggle the clicked dropdown
    const dropdown = document.getElementById(type + 'Dropdown');
    if (dropdown) {
        dropdown.classList.toggle('dropdown-active');

        // Update calendar when opening
        if (type === 'checkin' || type === 'checkout') {
            updateCalendarDisplay(type);
        }
    }
}

function navigateMonth(direction) {
    currentMonthIndex += direction;
    if (currentMonthIndex > 11) {
        currentMonthIndex = 0;
        currentYear++;
    } else if (currentMonthIndex < 0) {
        currentMonthIndex = 11;
        currentYear--;
    }
    updateCalendarDisplay('checkin');
}

function navigateMonthCheckout(direction) {
    currentMonthIndexCheckout += direction;
    if (currentMonthIndexCheckout > 11) {
        currentMonthIndexCheckout = 0;
        currentYearCheckout++;
    } else if (currentMonthIndexCheckout < 0) {
        currentMonthIndexCheckout = 11;
        currentYearCheckout--;
    }
    updateCalendarDisplay('checkout');
}

// Add this function to handle mobile single month navigation
function isMobileView() {
    return window.innerWidth <= 768;
}

// Update the updateCalendarDisplay function to handle mobile single month
function updateCalendarDisplay(type) {
    const isCheckout = type === 'checkout';
    const monthIndex = isCheckout ? currentMonthIndexCheckout : currentMonthIndex;
    const year = isCheckout ? currentYearCheckout : currentYear;
    const suffix = isCheckout ? 'Checkout' : '';

    // Calculate next month
    let nextMonthIndex = monthIndex + 1;
    let nextYear = year;
    if (nextMonthIndex > 11) {
        nextMonthIndex = 0;
        nextYear++;
    }

    // Update month titles
    const month1Title = document.getElementById(`month1Title${suffix}`);
    const month2Title = document.getElementById(`month2Title${suffix}`);

    if (month1Title) {
        month1Title.textContent = `${monthNames[monthIndex]} ${year}`;
    }

    // Only update second month title on desktop
    if (month2Title && !isMobileView()) {
        month2Title.textContent = `${monthNames[nextMonthIndex]} ${nextYear}`;
    }

    // Generate calendar days
    generateCalendarDays(monthIndex, year, `calendar1${suffix}`, type);

    // Only generate second calendar on desktop
    if (!isMobileView()) {
        generateCalendarDays(nextMonthIndex, nextYear, `calendar2${suffix}`, type);
    }
}

function generateCalendarDays(monthIndex, year, containerId, type) {
    // console.log('Generating calendar for:', containerId);
    const container = document.getElementById(containerId);
    // console.log('Container found:', container);
    if (!container) return;

    const grid = container.querySelector('.calendar-grid') || container;
    // if (!grid) return;

    // Clear existing days (keep headers)
    const headers = grid.querySelectorAll('.calendar-day-header');
    grid.innerHTML = '';
    headers.forEach(header => grid.appendChild(header));

    const firstDay = new Date(year, monthIndex, 1);
    const lastDay = new Date(year, monthIndex + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = (firstDay.getDay() + 6) % 7; // Adjust for Monday start

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day other-month';
        grid.appendChild(emptyDay);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        dayElement.textContent = day;
        dayElement.onclick = () => selectCalendarDate(day, monthIndex, year, type);

        // Highlight today
        const today = new Date();
        if (year === today.getFullYear() && monthIndex === today.getMonth() && day === today.getDate()) {
            dayElement.classList.add('bg-blue-100');
        }

        // Highlight selected dates (27th and 28th of June as default)
        if (year === 2025 && monthIndex === 5 && (day === 27 || day === 28)) {
            dayElement.classList.add('selected');
        }

        grid.appendChild(dayElement);
    }
}

function selectCalendarDate(day, monthIndex, year, type) {
    // Clear previous selections in this calendar
    const suffix = type === 'checkout' ? 'Checkout' : '';
    const calendars = [`calendar1${suffix}`, `calendar2${suffix}`];

    calendars.forEach(calId => {
        const cal = document.getElementById(calId);
        if (cal) {
            cal.querySelectorAll('.calendar-day.selected').forEach(el => {
                el.classList.remove('selected');
            });
        }
    });

    // Add selection to clicked date
    event.target.classList.add('selected');

    // Format date
    const dayStr = day.toString().padStart(2, '0');
    const monthStr = (monthIndex + 1).toString().padStart(2, '0');
    const yearStr = year.toString().slice(-2);

    // Get day of week
    const date = new Date(year, monthIndex, day);
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const dayOfWeek = dayNames[date.getDay()];

    const displayDate = `${dayOfWeek}, ${dayStr}/${monthStr}/${yearStr}`;

    // Update display
    if (type === 'checkin') {
        const checkinDiv = document.querySelector('[onclick="toggleDropdown(\'checkin\')"] .text-gray-800');
        if (checkinDiv) checkinDiv.textContent = displayDate;
    } else {
        const checkoutDiv = document.querySelector('[onclick="toggleDropdown(\'checkout\')"] .text-gray-800');
        if (checkoutDiv) checkoutDiv.textContent = displayDate;
    }

    toggleDropdown(type);
}

function selectQuickDate(option) {
    const today = new Date();
    let selectedDate;

    switch (option) {
        case 'tonight':
            selectedDate = today;
            break;
        case 'tomorrow':
            selectedDate = new Date(today);
            selectedDate.setDate(today.getDate() + 1);
            break;
        case 'weekend':
            selectedDate = new Date(today);
            const daysUntilSaturday = (6 - today.getDay()) % 7;
            selectedDate.setDate(today.getDate() + daysUntilSaturday);
            break;
        case 'nextweekend':
            selectedDate = new Date(today);
            const daysUntilNextSaturday = ((6 - today.getDay()) % 7) + 7;
            selectedDate.setDate(today.getDate() + daysUntilNextSaturday);
            break;
    }

    if (selectedDate) {
        selectCalendarDate(selectedDate.getDate(), selectedDate.getMonth(), selectedDate.getFullYear(), 'checkin');
    }
}

function selectQuickDateCheckout(option) {
    const today = new Date();
    let selectedDate;

    switch (option) {
        case 'tonight':
            selectedDate = new Date(today);
            selectedDate.setDate(today.getDate() + 1); // Checkout is typically next day
            break;
        case 'tomorrow':
            selectedDate = new Date(today);
            selectedDate.setDate(today.getDate() + 2);
            break;
        case 'weekend':
            selectedDate = new Date(today);
            const daysUntilSunday = (7 - today.getDay()) % 7;
            selectedDate.setDate(today.getDate() + daysUntilSunday);
            break;
        case 'nextweekend':
            selectedDate = new Date(today);
            const daysUntilNextSunday = ((7 - today.getDay()) % 7) + 7;
            selectedDate.setDate(today.getDate() + daysUntilNextSunday);
            break;
    }

    if (selectedDate) {
        selectCalendarDate(selectedDate.getDate(), selectedDate.getMonth(), selectedDate.getFullYear(), 'checkout');
    }
}

function selectLocation(name, subtitle) {
    const input = document.querySelector('input[value="Cape Town"]');
    if (input) {
        input.value = name;
    }
    toggleDropdown('location');
}

function incrementGuests(type) {
    if (type === 'adults' && guestCounts.adults < 10) {
        guestCounts.adults++;
    } else if (type === 'children' && guestCounts.children < 10) {
        guestCounts.children++;
    } else if (type === 'rooms' && guestCounts.rooms < 5) {
        guestCounts.rooms++;
    }

    document.getElementById(type + 'Count').textContent = guestCounts[type];
}

function decrementGuests(type) {
    if (type === 'adults' && guestCounts.adults > 1) {
        guestCounts.adults--;
    } else if (type === 'children' && guestCounts.children > 0) {
        guestCounts.children--;
    } else if (type === 'rooms' && guestCounts.rooms > 1) {
        guestCounts.rooms--;
    }

    document.getElementById(type + 'Count').textContent = guestCounts[type];
}

function resetGuests() {
    guestCounts = { adults: 1, children: 0, rooms: 1 };
    document.getElementById('adultsCount').textContent = guestCounts.adults;
    document.getElementById('childrenCount').textContent = guestCounts.children;
    document.getElementById('roomsCount').textContent = guestCounts.rooms;
    document.getElementById('petFriendly').checked = false;
}

function applyGuests() {
    const totalGuests = guestCounts.adults + guestCounts.children;
    const guestsText = `${totalGuests} Guest${totalGuests > 1 ? 's' : ''}, ${guestCounts.rooms} Room${guestCounts.rooms > 1 ? 's' : ''}`;

    const guestsDiv = document.querySelector('[onclick="toggleDropdown(\'guests\')"] .text-gray-800');
    if (guestsDiv) guestsDiv.textContent = guestsText;

    toggleDropdown('guests');
}

// Close dropdowns when clicking outside
document.addEventListener('click', function (event) {
    const dropdowns = ['locationDropdown', 'checkinDropdown', 'checkoutDropdown', 'guestsDropdown'];
    let clickedInsideDropdown = false;

    dropdowns.forEach(id => {
        const dropdown = document.getElementById(id);
        const trigger = dropdown?.previousElementSibling;

        if (dropdown?.contains(event.target) || trigger?.contains(event.target)) {
            clickedInsideDropdown = true;
        }
    });

    if (!clickedInsideDropdown) {
        dropdowns.forEach(id => {
            const dropdown = document.getElementById(id);
            if (dropdown) {
                dropdown.classList.remove('dropdown-active');
            }
        });
    }
});

// Country Data List Functionality
// Country data with popular countries first
const popularCountries = [
    { code: 'za', name: 'South Africa' },
    { code: 'us', name: 'United States' },
    { code: 'gb', name: 'United Kingdom' },
    { code: 'de', name: 'Germany' },
    { code: 'fr', name: 'France' },
    { code: 'es', name: 'Spain' },
    { code: 'it', name: 'Italy' },
    { code: 'au', name: 'Australia' },
    { code: 'ca', name: 'Canada' },
    { code: 'jp', name: 'Japan' }
];

// All countries (you can expand this list or use an API)
const allCountries = [
    { code: 'ad', name: 'Andorra' },
    { code: 'ae', name: 'United Arab Emirates' },
    { code: 'af', name: 'Afghanistan' },
    { code: 'ag', name: 'Antigua and Barbuda' },
    { code: 'ai', name: 'Anguilla' },
    { code: 'al', name: 'Albania' },
    { code: 'am', name: 'Armenia' },
    { code: 'ao', name: 'Angola' },
    { code: 'aq', name: 'Antarctica' },
    { code: 'ar', name: 'Argentina' },
    { code: 'as', name: 'American Samoa' },
    { code: 'at', name: 'Austria' },
    { code: 'au', name: 'Australia' },
    { code: 'aw', name: 'Aruba' },
    { code: 'ax', name: 'Åland Islands' },
    { code: 'az', name: 'Azerbaijan' },
    { code: 'ba', name: 'Bosnia and Herzegovina' },
    { code: 'bb', name: 'Barbados' },
    { code: 'bd', name: 'Bangladesh' },
    { code: 'be', name: 'Belgium' },
    { code: 'bf', name: 'Burkina Faso' },
    { code: 'bg', name: 'Bulgaria' },
    { code: 'bh', name: 'Bahrain' },
    { code: 'bi', name: 'Burundi' },
    { code: 'bj', name: 'Benin' },
    { code: 'bl', name: 'Saint Barthélemy' },
    { code: 'bm', name: 'Bermuda' },
    { code: 'bn', name: 'Brunei' },
    { code: 'bo', name: 'Bolivia' },
    { code: 'bq', name: 'Caribbean Netherlands' },
    { code: 'br', name: 'Brazil' },
    { code: 'bs', name: 'Bahamas' },
    { code: 'bt', name: 'Bhutan' },
    { code: 'bv', name: 'Bouvet Island' },
    { code: 'bw', name: 'Botswana' },
    { code: 'by', name: 'Belarus' },
    { code: 'bz', name: 'Belize' },
    { code: 'ca', name: 'Canada' },
    { code: 'cc', name: 'Cocos Islands' },
    { code: 'cd', name: 'Democratic Republic of the Congo' },
    { code: 'cf', name: 'Central African Republic' },
    { code: 'cg', name: 'Republic of the Congo' },
    { code: 'ch', name: 'Switzerland' },
    { code: 'ci', name: 'Côte d\'Ivoire' },
    { code: 'ck', name: 'Cook Islands' },
    { code: 'cl', name: 'Chile' },
    { code: 'cm', name: 'Cameroon' },
    { code: 'cn', name: 'China' },
    { code: 'co', name: 'Colombia' },
    { code: 'cr', name: 'Costa Rica' },
    { code: 'cu', name: 'Cuba' },
    { code: 'cv', name: 'Cape Verde' },
    { code: 'cw', name: 'Curaçao' },
    { code: 'cx', name: 'Christmas Island' },
    { code: 'cy', name: 'Cyprus' },
    { code: 'cz', name: 'Czech Republic' },
    { code: 'de', name: 'Germany' },
    { code: 'dj', name: 'Djibouti' },
    { code: 'dk', name: 'Denmark' },
    { code: 'dm', name: 'Dominica' },
    { code: 'do', name: 'Dominican Republic' },
    { code: 'dz', name: 'Algeria' },
    { code: 'ec', name: 'Ecuador' },
    { code: 'ee', name: 'Estonia' },
    { code: 'eg', name: 'Egypt' },
    { code: 'eh', name: 'Western Sahara' },
    { code: 'er', name: 'Eritrea' },
    { code: 'es', name: 'Spain' },
    { code: 'et', name: 'Ethiopia' },
    { code: 'fi', name: 'Finland' },
    { code: 'fj', name: 'Fiji' },
    { code: 'fk', name: 'Falkland Islands' },
    { code: 'fm', name: 'Micronesia' },
    { code: 'fo', name: 'Faroe Islands' },
    { code: 'fr', name: 'France' },
    { code: 'ga', name: 'Gabon' },
    { code: 'gb', name: 'United Kingdom' },
    { code: 'gd', name: 'Grenada' },
    { code: 'ge', name: 'Georgia' },
    { code: 'gf', name: 'French Guiana' },
    { code: 'gg', name: 'Guernsey' },
    { code: 'gh', name: 'Ghana' },
    { code: 'gi', name: 'Gibraltar' },
    { code: 'gl', name: 'Greenland' },
    { code: 'gm', name: 'Gambia' },
    { code: 'gn', name: 'Guinea' },
    { code: 'gp', name: 'Guadeloupe' },
    { code: 'gq', name: 'Equatorial Guinea' },
    { code: 'gr', name: 'Greece' },
    { code: 'gs', name: 'South Georgia' },
    { code: 'gt', name: 'Guatemala' },
    { code: 'gu', name: 'Guam' },
    { code: 'gw', name: 'Guinea-Bissau' },
    { code: 'gy', name: 'Guyana' },
    { code: 'hk', name: 'Hong Kong' },
    { code: 'hm', name: 'Heard Island and McDonald Islands' },
    { code: 'hn', name: 'Honduras' },
    { code: 'hr', name: 'Croatia' },
    { code: 'ht', name: 'Haiti' },
    { code: 'hu', name: 'Hungary' },
    { code: 'id', name: 'Indonesia' },
    { code: 'ie', name: 'Ireland' },
    { code: 'il', name: 'Israel' },
    { code: 'im', name: 'Isle of Man' },
    { code: 'in', name: 'India' },
    { code: 'io', name: 'British Indian Ocean Territory' },
    { code: 'iq', name: 'Iraq' },
    { code: 'ir', name: 'Iran' },
    { code: 'is', name: 'Iceland' },
    { code: 'it', name: 'Italy' },
    { code: 'je', name: 'Jersey' },
    { code: 'jm', name: 'Jamaica' },
    { code: 'jo', name: 'Jordan' },
    { code: 'jp', name: 'Japan' },
    { code: 'ke', name: 'Kenya' },
    { code: 'kg', name: 'Kyrgyzstan' },
    { code: 'kh', name: 'Cambodia' },
    { code: 'ki', name: 'Kiribati' },
    { code: 'km', name: 'Comoros' },
    { code: 'kn', name: 'Saint Kitts and Nevis' },
    { code: 'kp', name: 'North Korea' },
    { code: 'kr', name: 'South Korea' },
    { code: 'kw', name: 'Kuwait' },
    { code: 'ky', name: 'Cayman Islands' },
    { code: 'kz', name: 'Kazakhstan' },
    { code: 'la', name: 'Laos' },
    { code: 'lb', name: 'Lebanon' },
    { code: 'lc', name: 'Saint Lucia' },
    { code: 'li', name: 'Liechtenstein' },
    { code: 'lk', name: 'Sri Lanka' },
    { code: 'lr', name: 'Liberia' },
    { code: 'ls', name: 'Lesotho' },
    { code: 'lt', name: 'Lithuania' },
    { code: 'lu', name: 'Luxembourg' },
    { code: 'lv', name: 'Latvia' },
    { code: 'ly', name: 'Libya' },
    { code: 'ma', name: 'Morocco' },
    { code: 'mc', name: 'Monaco' },
    { code: 'md', name: 'Moldova' },
    { code: 'me', name: 'Montenegro' },
    { code: 'mf', name: 'Saint Martin' },
    { code: 'mg', name: 'Madagascar' },
    { code: 'mh', name: 'Marshall Islands' },
    { code: 'mk', name: 'North Macedonia' },
    { code: 'ml', name: 'Mali' },
    { code: 'mm', name: 'Myanmar' },
    { code: 'mn', name: 'Mongolia' },
    { code: 'mo', name: 'Macao' },
    { code: 'mp', name: 'Northern Mariana Islands' },
    { code: 'mq', name: 'Martinique' },
    { code: 'mr', name: 'Mauritania' },
    { code: 'ms', name: 'Montserrat' },
    { code: 'mt', name: 'Malta' },
    { code: 'mu', name: 'Mauritius' },
    { code: 'mv', name: 'Maldives' },
    { code: 'mw', name: 'Malawi' },
    { code: 'mx', name: 'Mexico' },
    { code: 'my', name: 'Malaysia' },
    { code: 'mz', name: 'Mozambique' },
    { code: 'na', name: 'Namibia' },
    { code: 'nc', name: 'New Caledonia' },
    { code: 'ne', name: 'Niger' },
    { code: 'nf', name: 'Norfolk Island' },
    { code: 'ng', name: 'Nigeria' },
    { code: 'ni', name: 'Nicaragua' },
    { code: 'nl', name: 'Netherlands' },
    { code: 'no', name: 'Norway' },
    { code: 'np', name: 'Nepal' },
    { code: 'nr', name: 'Nauru' },
    { code: 'nu', name: 'Niue' },
    { code: 'nz', name: 'New Zealand' },
    { code: 'om', name: 'Oman' },
    { code: 'pa', name: 'Panama' },
    { code: 'pe', name: 'Peru' },
    { code: 'pf', name: 'French Polynesia' },
    { code: 'pg', name: 'Papua New Guinea' },
    { code: 'ph', name: 'Philippines' },
    { code: 'pk', name: 'Pakistan' },
    { code: 'pl', name: 'Poland' },
    { code: 'pm', name: 'Saint Pierre and Miquelon' },
    { code: 'pn', name: 'Pitcairn Islands' },
    { code: 'pr', name: 'Puerto Rico' },
    { code: 'ps', name: 'Palestine' },
    { code: 'pt', name: 'Portugal' },
    { code: 'pw', name: 'Palau' },
    { code: 'py', name: 'Paraguay' },
    { code: 'qa', name: 'Qatar' },
    { code: 're', name: 'Réunion' },
    { code: 'ro', name: 'Romania' },
    { code: 'rs', name: 'Serbia' },
    { code: 'ru', name: 'Russia' },
    { code: 'rw', name: 'Rwanda' },
    { code: 'sa', name: 'Saudi Arabia' },
    { code: 'sb', name: 'Solomon Islands' },
    { code: 'sc', name: 'Seychelles' },
    { code: 'sd', name: 'Sudan' },
    { code: 'se', name: 'Sweden' },
    { code: 'sg', name: 'Singapore' },
    { code: 'sh', name: 'Saint Helena' },
    { code: 'si', name: 'Slovenia' },
    { code: 'sj', name: 'Svalbard and Jan Mayen' },
    { code: 'sk', name: 'Slovakia' },
    { code: 'sl', name: 'Sierra Leone' },
    { code: 'sm', name: 'San Marino' },
    { code: 'sn', name: 'Senegal' },
    { code: 'so', name: 'Somalia' },
    { code: 'sr', name: 'Suriname' },
    { code: 'ss', name: 'South Sudan' },
    { code: 'st', name: 'São Tomé and Príncipe' },
    { code: 'sv', name: 'El Salvador' },
    { code: 'sx', name: 'Sint Maarten' },
    { code: 'sy', name: 'Syria' },
    { code: 'sz', name: 'Eswatini' },
    { code: 'tc', name: 'Turks and Caicos Islands' },
    { code: 'td', name: 'Chad' },
    { code: 'tf', name: 'French Southern and Antarctic Lands' },
    { code: 'tg', name: 'Togo' },
    { code: 'th', name: 'Thailand' },
    { code: 'tj', name: 'Tajikistan' },
    { code: 'tk', name: 'Tokelau' },
    { code: 'tl', name: 'Timor-Leste' },
    { code: 'tm', name: 'Turkmenistan' },
    { code: 'tn', name: 'Tunisia' },
    { code: 'to', name: 'Tonga' },
    { code: 'tr', name: 'Turkey' },
    { code: 'tt', name: 'Trinidad and Tobago' },
    { code: 'tv', name: 'Tuvalu' },
    { code: 'tw', name: 'Taiwan' },
    { code: 'tz', name: 'Tanzania' },
    { code: 'ua', name: 'Ukraine' },
    { code: 'ug', name: 'Uganda' },
    { code: 'um', name: 'United States Minor Outlying Islands' },
    { code: 'us', name: 'United States' },
    { code: 'uy', name: 'Uruguay' },
    { code: 'uz', name: 'Uzbekistan' },
    { code: 'va', name: 'Vatican City' },
    { code: 'vc', name: 'Saint Vincent and the Grenadines' },
    { code: 've', name: 'Venezuela' },
    { code: 'vg', name: 'British Virgin Islands' },
    { code: 'vi', name: 'United States Virgin Islands' },
    { code: 'vn', name: 'Vietnam' },
    { code: 'vu', name: 'Vanuatu' },
    { code: 'wf', name: 'Wallis and Futuna' },
    { code: 'ws', name: 'Samoa' },
    { code: 'ye', name: 'Yemen' },
    { code: 'yt', name: 'Mayotte' },
    { code: 'za', name: 'South Africa' },
    { code: 'zm', name: 'Zambia' },
    { code: 'zw', name: 'Zimbabwe' }
];

let currentCountries = [];

// Initialize country selector
document.addEventListener('DOMContentLoaded', function () {
    initializeCountrySelector();
});

function initializeCountrySelector() {
    // Combine popular countries with all countries (remove duplicates)
    const popularCodes = popularCountries.map(c => c.code);
    const otherCountries = allCountries.filter(c => !popularCodes.includes(c.code));

    if (!carousel || carousel.length === 0) {
        console.log('No carousel elements found');
        return;
    }

    currentCountries = [
        ...popularCountries,
        { separator: true }, // Add separator
        ...otherCountries.sort((a, b) => a.name.localeCompare(b.name))
    ];

    renderCountryList();
}

function renderCountryList() {
    const countryList = document.getElementById('countryList');
    countryList.innerHTML = '';

    if (!countryList) return;

    currentCountries.forEach(country => {
        if (country.separator) {
            const separator = document.createElement('div');
            separator.className = 'country-separator';
            separator.innerHTML = '<hr style="border-color: #333; margin: 5px 0;">';
            countryList.appendChild(separator);
        } else {
            const option = document.createElement('div');
            option.className = 'country-option';
            option.onclick = () => selectCountry(country.code, country.name);

            option.innerHTML = `
                <span class="fi fi-${country.code} flag-icon"></span>
                <span class="country-name">${country.name}</span>
            `;

            countryList.appendChild(option);
        }
    });
}

function toggleCountryDropdown() {
    const dropdown = document.getElementById('countryDropdown');
    const selector = document.querySelector('.country-selector');

    if (dropdown.classList.contains('hidden')) {
        dropdown.classList.remove('hidden');
        dropdown.classList.add('show');
        selector.classList.add('active');
        document.getElementById('countrySearch').focus();
    } else {
        dropdown.classList.add('hidden');
        dropdown.classList.remove('show');
        selector.classList.remove('active');
        document.getElementById('countrySearch').value = '';
        renderCountryList(); // Reset list
    }
}

function selectCountry(code, name) {
    document.getElementById('selectedFlag').className = `fi fi-${code} flag-icon`;
    document.getElementById('selectedCountry').textContent = name;

    toggleCountryDropdown();

    // You can add additional logic here, like updating the website language/region
    // console.log(`Selected country: ${name} (${code})`);
}

function filterCountries() {
    const searchTerm = document.getElementById('countrySearch').value.toLowerCase();

    if (searchTerm === '') {
        renderCountryList();
        return;
    }

    const filteredCountries = allCountries.filter(country =>
        country.name.toLowerCase().includes(searchTerm)
    ).sort((a, b) => a.name.localeCompare(b.name));

    const countryList = document.getElementById('countryList');
    countryList.innerHTML = '';

    filteredCountries.forEach(country => {
        const option = document.createElement('div');
        option.className = 'country-option';
        option.onclick = () => selectCountry(country.code, country.name);

        option.innerHTML = `
            <span class="fi fi-${country.code} flag-icon"></span>
            <span class="country-name">${country.name}</span>
        `;

        countryList.appendChild(option);
    });
}

// Close dropdown when clicking outside
document.addEventListener('click', function (event) {
    const countrySelector = document.querySelector('.country-selector');
    if (!countrySelector.contains(event.target)) {
        const dropdown = document.getElementById('countryDropdown');
        if (!dropdown.classList.contains('hidden')) {
            toggleCountryDropdown();
        }
    }
});
// County List Functionality Ends Here

// Card Carousal Functionality

let currentSlide = 0;
let cardsPerView = 3;
let totalCards = 0;
let maxSlide = 0;

// Initialize carousel
document.addEventListener('DOMContentLoaded', function () {
    initializeCarousel();
    window.addEventListener('resize', initializeCarousel);
});

function initializeCarousel() {
    const carousel = document.getElementById('hotelCarousel');
    const cards = carousel.querySelectorAll('.flex-none');
    totalCards = cards.length;

    if (!carousel || carousel.length === 0) {
        console.log('No carousel elements found');
        return;
    }
    // Determine cards per view based on screen size
    if (window.innerWidth < 768) {
        cardsPerView = 1;
    } else if (window.innerWidth < 1024) {
        cardsPerView = 2;
    } else {
        cardsPerView = 3;
    }

    maxSlide = Math.max(0, totalCards - cardsPerView);

    // Reset to first slide if current slide is beyond max
    if (currentSlide > maxSlide) {
        currentSlide = maxSlide;
    }

    updateCarousel();
    updateNavigationButtons();
    createIndicators();
}

function slideCarousel(direction) {
    currentSlide += direction;

    // Ensure we don't go beyond bounds
    if (currentSlide < 0) {
        currentSlide = 0;
    } else if (currentSlide > maxSlide) {
        currentSlide = maxSlide;
    }

    updateCarousel();
    updateNavigationButtons();
    updateIndicators();
}

function updateCarousel() {
    const carousel = document.getElementById('hotelCarousel');
    let translateX = 0;

    if (window.innerWidth < 768) {
        // Mobile: Calculate based on card width including padding
        // Each card is 100% width with 24px total padding (12px each side)
        const cardWidth = carousel.parentElement.offsetWidth;
        translateX = -(currentSlide * cardWidth);
        carousel.style.transform = `translateX(${translateX}px)`;
    } else if (window.innerWidth < 1024) {
        // Tablet: 50% width per card
        translateX = -(currentSlide * 50);
        carousel.style.transform = `translateX(${translateX}%)`;
    } else {
        // Desktop: 33.333% width per card
        translateX = -(currentSlide * (100 / 3));
        carousel.style.transform = `translateX(${translateX}%)`;
    }
}

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    // Update previous button
    if (currentSlide <= 0) {
        prevBtn.classList.add('opacity-50', 'cursor-not-allowed');
        prevBtn.classList.remove('hover:bg-gray-50');
    } else {
        prevBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        prevBtn.classList.add('hover:bg-gray-50');
    }

    // Update next button
    if (currentSlide >= maxSlide) {
        nextBtn.classList.add('opacity-50', 'cursor-not-allowed');
        nextBtn.classList.remove('hover:bg-gray-50');
    } else {
        nextBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        nextBtn.classList.add('hover:bg-gray-50');
    }
}

function createIndicators() {
    const indicatorContainer = document.getElementById('indicators');
    indicatorContainer.innerHTML = '';

    // Only show indicators if there are more slides than can be viewed
    if (maxSlide > 0) {
        for (let i = 0; i <= maxSlide; i++) {
            const indicator = document.createElement('button');
            indicator.className = `w-2 h-2 rounded-full transition-colors duration-200 ${i === currentSlide ? 'bg-blue-600' : 'bg-gray-300'
                }`;
            indicator.onclick = () => goToSlide(i);
            indicatorContainer.appendChild(indicator);
        }
    }
}

function updateIndicators() {
    const indicators = document.querySelectorAll('#indicators button');
    indicators.forEach((indicator, index) => {
        if (index === currentSlide) {
            indicator.className = 'w-2 h-2 rounded-full transition-colors duration-200 bg-blue-600';
        } else {
            indicator.className = 'w-2 h-2 rounded-full transition-colors duration-200 bg-gray-300';
        }
    });
}

function goToSlide(slideIndex) {
    currentSlide = slideIndex;
    updateCarousel();
    updateNavigationButtons();
    updateIndicators();
}

// Touch/Swipe support for mobile
let startX = 0;
let endX = 0;

document.getElementById('hotelCarousel').addEventListener('touchstart', function (e) {
    startX = e.touches[0].clientX;
});

document.getElementById('hotelCarousel').addEventListener('touchend', function (e) {
    endX = e.changedTouches[0].clientX;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = startX - endX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe left - next slide
            slideCarousel(1);
        } else {
            // Swipe right - previous slide
            slideCarousel(-1);
        }
    }
}
// Card Carousal Functionality Ends Here

// Main Modal Functions
function showLoginModal(action = 'general') {
    const modal = document.getElementById('loginModal');
    const message = document.getElementById('modalMessage');

    // Customize message based on action
    const messages = {
        'general': 'Please sign in to your account to access this feature and enjoy exclusive benefits.',
        'favorite': 'Please sign in to save hotels to your favorites and create your personal wishlist.',
        'booking': 'Please sign in to complete your booking and access member-only deals.',
        'deals': 'Please sign in to view exclusive member deals and special offers.'
    };

    message.textContent = messages[action] || messages['general'];

    modal.classList.remove('hidden');
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    modal.classList.add('hidden');
    // Restore body scroll
    document.body.style.overflow = 'auto';
}

// Compact Modal Functions
function showCompactModal() {
    const modal = document.getElementById('compactModal');
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeCompactModal() {
    const modal = document.getElementById('compactModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

// Redirect Functions (customize these URLs)
function redirectToLogin() {
    window.location.href = "./login";
    closeLoginModal();
    closeCompactModal();
}

function redirectToSignup() {
    window.location.href = "./register";
    closeLoginModal();
}

// Close modals when clicking outside
document.getElementById('loginModal').addEventListener('click', function (e) {
    if (e.target === this) {
        closeLoginModal();
    }
});

document.getElementById('compactModal').addEventListener('click', function (e) {
    if (e.target === this) {
        closeCompactModal();
    }
});

// Close modals with Escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeLoginModal();
        closeCompactModal();
    }
});

// Example usage functions you can call from other pages
window.requireLogin = function (action) {
    showLoginModal(action);
};

window.showQuickLoginPrompt = function () {
    showCompactModal();
};

let countdownTimer = null;
let redirectTimer = null;
let compactCountdownTimer = null;
let compactRedirectTimer = null;

// Main Modal Functions
function showRedirectModal(action = 'general') {
    const modal = document.getElementById('redirectModal');
    const title = document.getElementById('redirectTitle');
    const message = document.getElementById('redirectMessage');

    // Customize message based on action
    const content = {
        'general': {
            title: 'Ready to explore amazing deals?',
            message: 'You\'ll be taken to Trivago.com where you can compare prices from hundreds of travel sites and find the perfect hotel at the best price.'
        },
        'booking': {
            title: 'Complete your booking on Trivago',
            message: 'You\'ll be redirected to Trivago.com to finalize your hotel reservation and secure the best available rate.'
        },
        'deals': {
            title: 'Discover exclusive deals on Trivago',
            message: 'You\'ll be taken to Trivago.com to explore thousands of hotel deals and limited-time offers from top booking sites.'
        },
        'search': {
            title: 'Continue your search on Trivago',
            message: 'You\'ll be redirected to Trivago.com to access our full search functionality and compare prices from over 100 booking sites.'
        }
    };

    const selectedContent = content[action] || content['general'];
    title.textContent = selectedContent.title;
    message.textContent = selectedContent.message;

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Start countdown
    startCountdown();
}

function closeRedirectModal() {
    const modal = document.getElementById('redirectModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';

    // Clear timers
    if (countdownTimer) clearInterval(countdownTimer);
    if (redirectTimer) clearTimeout(redirectTimer);
}

function startCountdown() {
    let seconds = 5;
    const countdownElement = document.getElementById('countdown');

    countdownTimer = setInterval(() => {
        seconds--;
        countdownElement.textContent = seconds;

        if (seconds <= 0) {
            clearInterval(countdownTimer);
            redirectNow();
        }
    }, 1000);
}

function redirectNow() {
    // Close modal first
    closeRedirectModal();

    // Redirect to Trivago
    window.open('https://www.trivago.com', '_blank');
    // Or use window.location.href = 'https://www.trivago.com' for same tab
}

// Compact Modal Functions
function showCompactRedirectModal() {
    const modal = document.getElementById('compactRedirectModal');
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Start compact countdown
    startCompactCountdown();
}

function closeCompactRedirectModal() {
    const modal = document.getElementById('compactRedirectModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';

    // Clear timers
    if (compactCountdownTimer) clearInterval(compactCountdownTimer);
    if (compactRedirectTimer) clearTimeout(compactRedirectTimer);
}

function startCompactCountdown() {
    let seconds = 5;
    const countdownElement = document.getElementById('compactCountdown');

    compactCountdownTimer = setInterval(() => {
        seconds--;
        countdownElement.textContent = seconds;

        if (seconds <= 0) {
            clearInterval(compactCountdownTimer);
            redirectNowCompact();
        }
    }, 1000);
}

function redirectNowCompact() {
    closeCompactRedirectModal();
    window.open('https://www.trivago.com', '_blank');
}

// Close modals when clicking outside
document.getElementById('redirectModal').addEventListener('click', function (e) {
    if (e.target === this) {
        closeRedirectModal();
    }
});

document.getElementById('compactRedirectModal').addEventListener('click', function (e) {
    if (e.target === this) {
        closeCompactRedirectModal();
    }
});

// Close modals with Escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeRedirectModal();
        closeCompactRedirectModal();
    }
});

// Global functions for easy integration
window.redirectToTrivago = function (action) {
    showRedirectModal(action);
};

window.quickRedirectToTrivago = function () {
    showCompactRedirectModal();
};

// Login/Signup Functions
