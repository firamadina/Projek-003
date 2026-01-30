# To-do List sederhana (tanpa import module)
# Fitur:
# 1. Menyimpan, mengedit, menghapus data tugas/kegiatan/acara
# 2. Melihat data yang tersimpan dan memperbarui data yang sudah dihapus/diedit (restore & riwayat)
# 3. Status tugas (selesai / belum selesai)
# 4. Input tanggal (hari/bulan/tahun)

# Struktur data tiap tugas:
# {
#   'id': int,
#   'title': str,
#   'desc': str,
#   'date': {'day': int, 'month': int, 'year': int},
#   'status': 'selesai' or 'belum',
#   'deleted': bool,
#   'history': [previous_versions]
# }

DB_FILE = 'tasks.db'

# ---------------- helper ----------------

def next_id(tasks):
    if not tasks:
        return 1
    return max(t['id'] for t in tasks) + 1


def input_nonempty(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print('Masukan tidak boleh kosong. Coba lagi.')


def input_int_in_range(prompt, min_v, max_v):
    while True:
        v = input(prompt).strip()
        if not v.isdigit():
            print('Masukan harus angka. Coba lagi.')
            continue
        n = int(v)
        if n < min_v or n > max_v:
            print(f'Nilai harus antara {min_v} dan {max_v}.')
            continue
        return n


def input_date():
    print('Masukan tanggal:')
    day = input_int_in_range('  Hari (1-31): ', 1, 31)
    month = input_int_in_range('  Bulan (1-12): ', 1, 12)
    year = input_int_in_range('  Tahun (misal 2026): ', 1, 9999)
    return {'day': day, 'month': month, 'year': year}


def format_date(d):
    return f"{d['day']:02d}/{d['month']:02d}/{d['year']}"


def show_task_row(t):
    status = t['status']
    del_mark = ' (DIHAPUS)' if t.get('deleted') else ''
    print(f"[{t['id']}] {t['title']}{del_mark} - {format_date(t['date'])} - {status}")


def find_task(tasks, tid):
    for t in tasks:
        if t['id'] == tid:
            return t
    return None


# ---------------- penyimpanan ke file sederhana ----------------

def save_tasks(tasks):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            f.write(repr(tasks))
        print('Berhasil menyimpan ke disk.')
    except Exception as e:
        print('Gagal menyimpan:', e)


def load_tasks():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = f.read()
            if not data.strip():
                return []
            tasks = eval(data)  # data lokal; untuk kesederhanaan digunakan eval
            return tasks
    except FileNotFoundError:
        return []
    except Exception as e:
        print('Gagal memuat data:', e)
        return []


# ---------------- operasi utama ----------------

def add_task(tasks):
    print('\n=== Tambah Tugas/Kegiatan/Acara ===')
    title = input_nonempty('Judul: ')
    desc = input('Deskripsi (bisa kosong): ').strip()
    date = input_date()
    t = {
        'id': next_id(tasks),
        'title': title,
        'desc': desc,
        'date': date,
        'status': 'belum',
        'deleted': False,
        'history': []
    }
    tasks.append(t)
    print('Tugas ditambahkan dengan ID', t['id'])


def list_all(tasks, include_deleted=True):
    print('\n=== Daftar Tugas ===')
    listed = False
    for t in sorted(tasks, key=lambda x: x['id']):
        if not include_deleted and t.get('deleted'):
            continue
        show_task_row(t)
        listed = True
    if not listed:
        print('Tidak ada tugas.')


def view_details(tasks):
    tid = input_int_in_range('Masukan ID tugas: ', 1, 10_000_000)
    t = find_task(tasks, tid)
    if not t:
        print('Tugas tidak ditemukan.')
        return
    print('\n--- Detail Tugas ---')
    print('ID:', t['id'])
    print('Judul:', t['title'])
    print('Deskripsi:', t['desc'] if t['desc'] else '-')
    print('Tanggal:', format_date(t['date']))
    print('Status:', t['status'])
    print('Dihapus?:', 'Ya' if t.get('deleted') else 'Tidak')
    print('Riwayat edit:', len(t.get('history', [])))


def edit_task(tasks):
    tid = input_int_in_range('Masukan ID tugas yang akan diedit: ', 1, 10_000_000)
    t = find_task(tasks, tid)
    if not t:
        print('Tugas tidak ditemukan.')
        return
    # simpan snapshot ke riwayat
    snapshot = {
        'title': t['title'],
        'desc': t['desc'],
        'date': t['date'].copy(),
        'status': t['status']
    }
    t.setdefault('history', []).append(snapshot)
    print('\nMasukan nilai baru (biarkan kosong untuk tidak mengubah):')
    new_title = input('  Judul [{}]: '.format(t['title'])).strip()
    if new_title:
        t['title'] = new_title
    new_desc = input('  Deskripsi [{}]: '.format(t['desc'] if t['desc'] else '-')).strip()
    if new_desc != '':
        t['desc'] = new_desc
    print('  Tanggal sekarang:', format_date(t['date']))
    if input('  Ubah tanggal? (y/n): ').lower().startswith('y'):
        t['date'] = input_date()
    if input('  Tandai selesai? (y/n): ').lower().startswith('y'):
        t['status'] = 'selesai'
    else:
        if input('  Tandai belum selesai? (y/n): ').lower().startswith('y'):
            t['status'] = 'belum'
    print('Tugas telah diperbarui dan riwayat disimpan.')


def delete_task(tasks):
    tid = input_int_in_range('Masukan ID tugas yang akan dihapus (ke trash): ', 1, 10_000_000)
    t = find_task(tasks, tid)
    if not t:
        print('Tugas tidak ditemukan.')
        return
    if t.get('deleted'):
        print('Tugas sudah berada di trash.')
        return
    t['deleted'] = True
    print('Tugas dipindahkan ke trash.')


def restore_task(tasks):
    tid = input_int_in_range('Masukan ID tugas yang akan dipulihkan: ', 1, 10_000_000)
    t = find_task(tasks, tid)
    if not t:
        print('Tugas tidak ditemukan.')
        return
    if not t.get('deleted'):
        print('Tugas tidak di-trash.')
        return
    t['deleted'] = False
    print('Tugas dipulihkan.')


def purge_task(tasks):
    tid = input_int_in_range('Masukan ID tugas yang akan dihapus permanen: ', 1, 10_000_000)
    for i, t in enumerate(tasks):
        if t['id'] == tid:
            confirm = input('Yakin ingin menghapus permanen? (ketik "hapus") : ').strip()
            if confirm == 'hapus':
                tasks.pop(i)
                print('Tugas dihapus permanen.')
            else:
                print('Dibatalkan.')
            return
    print('Tugas tidak ditemukan.')


def toggle_status(tasks):
    tid = input_int_in_range('Masukan ID tugas: ', 1, 10_000_000)
    t = find_task(tasks, tid)
    if not t:
        print('Tugas tidak ditemukan.')
        return
    if t['status'] == 'belum':
        t['status'] = 'selesai'
        print('Tugas ditandai selesai.')
    else:
        t['status'] = 'belum'
        print('Tugas ditandai belum selesai.')


def view_history(tasks):
    tid = input_int_in_range('Masukan ID tugas: ', 1, 10_000_000)
    t = find_task(tasks, tid)
    if not t:
        print('Tugas tidak ditemukan.')
        return
    h = t.get('history', [])
    if not h:
        print('Tidak ada riwayat.')
        return
    print('\n--- Riwayat (dari terlama ke terbaru) ---')
    for i, s in enumerate(h, 1):
        print(f"[{i}] {s['title']} - {format_date(s['date'])} - {s['status']}")
    if input('Kembalikan ke versi sebelumnya? (y/n): ').lower().startswith('y'):
        idx = input_int_in_range('Masukan nomor versi (1..{}): '.format(len(h)), 1, len(h)) - 1
        snap = h[idx]
        # simpan snapshot sekarang ke history
        current = {'title': t['title'], 'desc': t['desc'], 'date': t['date'].copy(), 'status': t['status']}
        t.setdefault('history', []).append(current)
        t['title'] = snap['title']
        t['desc'] = snap['desc']
        t['date'] = snap['date']
        t['status'] = snap['status']
        print('Versi telah dikembalikan.')


# ---------------- menu ----------------

def main_menu():
    tasks = load_tasks()
    while True:
        print('\n=== TO-DO LIST MENU ===')
        print('1. Tambah tugas/kegiatan/acara')
        print('2. Lihat semua data (termasuk yang dihapus)')
        print('3. Lihat data aktif (tidak dihapus)')
        print('4. Lihat data terhapus (trash)')
        print('5. Lihat detail & riwayat tugas')
        print('6. Edit tugas')
        print('7. Hapus tugas (ke trash)')
        print('8. Pulihkan tugas dari trash')
        print('9. Hapus permanen tugas')
        print('10. Tandai selesai/belum selesai')
        print('11. Simpan ke disk')
        print('12. Muat dari disk')
        print('0. Keluar')

        choice = input('Pilih nomor: ').strip()
        if choice == '1':
            add_task(tasks)
        elif choice == '2':
            list_all(tasks, include_deleted=True)
        elif choice == '3':
            list_all(tasks, include_deleted=False)
        elif choice == '4':
            print('\n=== Trash ===')
            any_trash = False
            for t in tasks:
                if t.get('deleted'):
                    show_task_row(t)
                    any_trash = True
            if not any_trash:
                print('Trash kosong.')
        elif choice == '5':
            view_details(tasks)
            if input('Lihat riwayat/edit? (y/n): ').lower().startswith('y'):
                view_history(tasks)
        elif choice == '6':
            edit_task(tasks)
        elif choice == '7':
            delete_task(tasks)
        elif choice == '8':
            restore_task(tasks)
        elif choice == '9':
            purge_task(tasks)
        elif choice == '10':
            toggle_status(tasks)
        elif choice == '11':
            save_tasks(tasks)
        elif choice == '12':
            tasks = load_tasks()
            print('Data dimuat dari disk.')
        elif choice == '0':
            if input('Simpan sebelum keluar? (y/n): ').lower().startswith('y'):
                save_tasks(tasks)
            print('Sampai jumpa!')
            break
        else:
            print('Pilihan tidak dikenal. Coba lagi.')


if __name__ == '__main__':
    main_menu()
