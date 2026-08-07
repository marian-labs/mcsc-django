import datetime
from django.forms import widgets

class Split12HourTimeWidget(widgets.MultiWidget):
    """
    A 12-hour time widget with a text box for 'hh:mm' (e.g. 02:20) and a dropdown for AM/PM.
    """
    def __init__(self, attrs=None):
        _widgets = (
            widgets.TextInput(attrs={'placeholder': '02:20', 'style': 'width: 80px; display: inline-block;', 'class': 'vTimeField'}),
            widgets.Select(choices=[('AM', 'AM'), ('PM', 'PM')], attrs={'style': 'display: inline-block; margin-left: 4px; padding: 3px 6px;'}),
        )
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, str):
                try:
                    t = datetime.datetime.strptime(value, '%H:%M:%S').time()
                except ValueError:
                    try:
                        t = datetime.datetime.strptime(value, '%H:%M').time()
                    except ValueError:
                        return ['', 'AM']
            elif isinstance(value, (datetime.time, datetime.datetime)):
                t = value if isinstance(value, datetime.time) else value.time()
            else:
                return ['', 'AM']
            
            hour = t.hour
            minute = t.minute
            meridiem = 'AM'
            if hour >= 12:
                meridiem = 'PM'
                if hour > 12:
                    hour -= 12
            elif hour == 0:
                hour = 12
            
            return [f"{hour:02d}:{minute:02d}", meridiem]
        return ['', 'AM']

    def value_from_datadict(self, data, files, name):
        vals = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)
        ]
        time_str, meridiem = vals[0], vals[1]
        if not time_str or not time_str.strip():
            return None
        
        time_str = time_str.strip()
        try:
            parts = time_str.split(':')
            if len(parts) >= 2:
                h = int(parts[0])
                m = int(parts[1])
                s = int(parts[2]) if len(parts) > 2 else 0
            else:
                return None
            
            if meridiem == 'PM' and h < 12:
                h += 12
            elif meridiem == 'AM' and h == 12:
                h = 0
            
            return datetime.time(h, m, s).strftime('%H:%M:%S')
        except (ValueError, TypeError):
            return time_str


class Split12HourDateTimeWidget(widgets.MultiWidget):
    """
    A 12-hour datetime widget with a date input, text box for 'hh:mm', and a dropdown for AM/PM.
    """
    def __init__(self, attrs=None):
        _widgets = (
            widgets.DateInput(attrs={'type': 'date', 'style': 'width: 140px; display: inline-block;', 'class': 'vDateField'}),
            widgets.TextInput(attrs={'placeholder': '02:20', 'style': 'width: 80px; display: inline-block; margin-left: 4px;', 'class': 'vTimeField'}),
            widgets.Select(choices=[('AM', 'AM'), ('PM', 'PM')], attrs={'style': 'display: inline-block; margin-left: 4px; padding: 3px 6px;'}),
        )
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, str):
                try:
                    dt = datetime.datetime.fromisoformat(value)
                except ValueError:
                    return ['', '', 'AM']
            elif isinstance(value, datetime.datetime):
                dt = value
            else:
                return ['', '', 'AM']
            
            d_str = dt.strftime('%Y-%m-%d')
            hour = dt.hour
            minute = dt.minute
            meridiem = 'AM'
            if hour >= 12:
                meridiem = 'PM'
                if hour > 12:
                    hour -= 12
            elif hour == 0:
                hour = 12
            
            t_str = f"{hour:02d}:{minute:02d}"
            return [d_str, t_str, meridiem]
        return ['', '', 'AM']

    def value_from_datadict(self, data, files, name):
        vals = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)
        ]
        date_str, time_str, meridiem = vals[0], vals[1], vals[2]
        if not date_str or not date_str.strip():
            return [None, None]
        
        date_str = date_str.strip()
        if not time_str or not time_str.strip():
            return [date_str, '00:00:00']
        
        time_str = time_str.strip()
        try:
            parts = time_str.split(':')
            if len(parts) >= 2:
                h = int(parts[0])
                m = int(parts[1])
                s = int(parts[2]) if len(parts) > 2 else 0
            else:
                h, m, s = 0, 0, 0
            
            if meridiem == 'PM' and h < 12:
                h += 12
            elif meridiem == 'AM' and h == 12:
                h = 0
            
            return [date_str, f"{h:02d}:{m:02d}:{s:02d}"]
        except (ValueError, TypeError):
            return [date_str, time_str]
