from rest_framework.views import APIView
from rest_framework.response import Response
import math


class PostProcView(APIView):

    def largest_remainder(self, options, q, points):
        out = []
        e = []
        r = []

        if len(options) == 0:
            raise(Exception('Bad request: There are no options'))

        for opt in options:
            ei = math.floor(opt['votes'] / q)
            e.append(ei)
            r.append(opt['votes'] - q * ei)

        k = points - sum(e)

        for x in range(k):
            grtst_rest_index = r.index(max(r))
            e[grtst_rest_index] = e[grtst_rest_index] + 1
            r[grtst_rest_index] = -1

        cont = 0
        for opt in options:
            out.append({
                **opt,
                'postproc': e[cont],
            })
            cont += 1

        out.sort(key=lambda x: (-x['postproc'], -x['votes']))
        return out

    def identity(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes'],
            })

        out.sort(key=lambda x: -x['postproc'])
        return out

    def borda(self, options):
        out = []

        if len(options) == 0:
            raise(Exception('Bad request: There no options'))

        for opt in options:
            votes = 0
            options_number = len(options)
            for i in range(0, options_number):
                votes += opt['votes'][i] * (options_number - i)
            out.append({
                **opt,
                'postproc': votes,
            })

        out.sort(key=lambda x: -x['postproc'])
        return out

    def equality(self, options):
        out = []
        n_women = 0
        n_men = 0

        if len(options) == 0:
            raise(Exception('Bad request: There are no options'))

        for opt in options:
            n_women += opt['votes_fem']
            n_men += opt['votes_masc']
        
        if n_men == 0 or n_women == 0:
            for opt in options:
                votes = opt['votes_fem'] + opt['votes_masc']
                out.append({
                    **opt,
                    'postproc': votes,
                })
        else:
            for opt in options:
                if n_women > n_men:
                    votes = opt['votes_masc'] + opt['votes_fem'] * (n_men / n_women)
                else:
                    votes = opt['votes_fem'] + opt['votes_masc'] * (n_women / n_men)

                out.append({
                    **opt,
                    'postproc': round(votes),
                })

        out.sort(key=lambda x: -x['postproc'])

        return out

    def droop(self, options):
        total_votes = 0
        points = None

        for opt in options:
            if points is None: points = opt['points']
            total_votes += opt['votes']

        q = round(1 + total_votes / (points + 1))

        return self.largest_remainder(options, q, points)

    def proportional_representation(self, options, type):
        out = []
        votes = []
        points_for_opt = []
        multiplier = 2 if type == 'SAINTE_LAGUE' else 1
        points = options[0]['points']
        zero_votes = True

        for i in range(0, len(options)):
            votes.append(options[i]['votes'])
            points_for_opt.append(0)
            if zero_votes is True and options[i]['votes'] != 0:
                zero_votes = False

        if zero_votes is False:
            for i in range(0, points):
                max_index = votes.index(max(votes))
                points_for_opt[max_index] += 1
                votes[max_index] = options[max_index]['votes'] / (multiplier * points_for_opt[max_index] + 1)

        for i in range(0, len(options)):
            out.append({
                **options[i],
                'postproc': points_for_opt[i],
            })

        out.sort(key=lambda x: (-x['postproc'], -x['votes']))
        return out

    def imperiali(self, options):
        total_votes = 0
        points = None

        for opt in options:
            if points is None: points = opt['points']
            total_votes += opt['votes']

        q = round(total_votes / (points + 2))

        return self.largest_remainder(options, q, points)

    def hare(self, options):
        total_votes = 0
        points = None

        for opt in options:
            if points is None: points = opt['points']
            total_votes += opt['votes']

        q = round(total_votes / points)

        return self.largest_remainder(options, q, points)

    def post(self, request):
        out = []
        questions = request.data

        for q in questions:
            result = None
            t = q['type']
            opts = q['options']

            if t == 'IDENTITY':
                result = self.identity(opts)
            if t == 'BORDA':
                result = self.borda(opts)
            if t == 'EQUALITY':
                result = self.equality(opts)
            if t == 'SAINTE_LAGUE' or t == 'HONDT':
                result = self.proportional_representation(opts, t)
            if t == 'DROOP':
                result = self.droop(opts)
            if t == 'IMPERIALI':
                result = self.imperiali(opts)
            if t == 'HARE':
                result = self.hare(opts)

            out.append({'type': t, 'options': result})


        return Response(out)