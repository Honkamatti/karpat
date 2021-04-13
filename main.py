import pandas as pd
import numpy as np
from unidecode import unidecode
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/send', methods=['POST'])
def send():
    features = request.form.values()
    name = list(features)[0]

    tableau = pd.read_csv('data_table.csv')
    tableau['plain_names'] = tableau.Name.apply(unidecode).str.lower()
    plain_name = unidecode(name).lower()

    if (tableau['plain_names'] == plain_name).any():
        onerow = pd.Series(tableau[tableau['plain_names'] == plain_name].iloc[0, :].T)
        name_label = 'Nimi: '
        true_name = onerow.Name
        age = 'Ikä: ' + str(int(onerow.Age))
        epid = onerow.EP_id
        eplink = 'https://www.eliteprospects.com/player/' + epid
        prediction = 'Ennuste: ' + '{:.2f}'.format(onerow.prediction) + ' pistettä / peli'
        season = onerow.Season

        previous_seasons = []
        for season_nr in np.arange(1, 6):
            labels = ['GP', 'PPG', 'GPG', 'APG', 'League']
            row = onerow.loc[
                [f'gp_{season_nr}', f'ppg_{season_nr}', f'gpg_{season_nr}', f'apg_{season_nr}', f'll_{season_nr}']].copy()
            row.index = labels
            previous_seasons.append(row)

        previous_seasons = pd.concat(previous_seasons, axis=1).T
        newindex = list(np.arange(season - 1, season - 6, -1))
        previous_seasons.index = newindex
        previous_seasons['GP'] = previous_seasons['GP'].astype(int)
        for column in ['GPG', 'PPG', 'APG', 'League']:
            previous_seasons[column] = previous_seasons[column].apply('{:.2f}'.format)
        headings = previous_seasons.columns
        data = previous_seasons.values
        errormessages = ''
        players = ['']
        tables = ['']
    else:
        name_label = ''
        true_name = 'Ei löytynyt'
        age = ''
        eplink = 'https://www.eliteprospects.com/'
        prediction = ''
        headings = []
        data = []
        errormessages = [f'Pelaajaa {name} ei löytynyt',
                         'Varmista että kirjoitit nimen oikein: Etunimi Sukunimi',
                         'Kuka tahansa pelaaja, joka on pelannut missään päin maailmaa viimeisten 5v aikana.']
        players = ''
        tables = ''
    return render_template('index.html',
                           name_label=name_label,
                           true_name=true_name,
                           age=age,
                           eplink=eplink,
                           prediction=prediction,
                           headings=headings,
                           data=data,
                           errormessages=errormessages,
                           players=players,
                           tables=tables)

@app.errorhandler(404)
def page_not_found(e):
    errormessages = ['Anteeksi!', 'Nyt meni jotain pieleen, mutta yritä uudelleen']
    return render_template('index.html', errormessages=errormessages), 404

@app.errorhandler(403)
def not_possible(e):
    errormessages = ['Anteeksi!', 'Nyt meni jotain pieleen, mutta yritä uudelleen']
    return render_template('index.html', errormessages=errormessages), 403

@app.errorhandler(405)
def forbidden(e):
    errormessages = ['Anteeksi!', 'Nyt meni jotain pieleen, mutta yritä uudelleen']
    return render_template('index.html', errormessages=errormessages), 405

@app.errorhandler(500)
def internal_server_error(e):
    errormessages = ['Anteeksi!', 'Nyt meni jotain pieleen, mutta yritä uudelleen']
    return render_template('index.html', errormessages=errormessages), 500

if __name__ == "__main__":
    app.run()

