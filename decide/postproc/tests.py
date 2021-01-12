from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods


class PostProcTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)

    def tearDown(self):
        self.client = None

    def test_identity(self):
        data = [{
            'type': 'IDENTITY',
            'options': [
                { 'option': 'Option 1', 'number': 1, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 5 },
                { 'option': 'Option 2', 'number': 2, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0 },
                { 'option': 'Option 3', 'number': 3, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 3 },
                { 'option': 'Option 4', 'number': 4, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 2 },
                { 'option': 'Option 5', 'number': 5, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 5 },
                { 'option': 'Option 6', 'number': 6, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 1 },
            ]
        }]

        expected_result = [{
            'type': 'IDENTITY',
            'options': [
                { 'option': 'Option 1', 'number': 1, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 5, 'postproc': 5 },
                { 'option': 'Option 5', 'number': 5, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 5, 'postproc': 5 },
                { 'option': 'Option 3', 'number': 3, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 3, 'postproc': 3 },
                { 'option': 'Option 4', 'number': 4, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 2, 'postproc': 2 },
                { 'option': 'Option 6', 'number': 6, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 1, 'postproc': 1 },
                { 'option': 'Option 2', 'number': 2, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 0 },
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_identity_multiple_questions(self):
        data = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 5},
                {'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0},
                {'option': 'Option 3', 'number': 3, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 3}
            ]
        }, {
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 2},
                {'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 5},
                {'option': 'Option 3', 'number': 3, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 1}
            ]
        }]

        expected_result = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 5, 'postproc': 5},
                {'option': 'Option 3', 'number': 3, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 3, 'postproc': 3},
                {'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0, 'postproc': 0}
            ]
        }, {
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 5, 'postproc': 5},
                {'option': 'Option 1', 'number': 1, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 2, 'postproc': 2},
                {'option': 'Option 3', 'number': 3, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 1, 'postproc': 1}
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_borda(self):
        data = [{
            'type': 'BORDA',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [7,2,4,2]},
                {'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [2,8,2,3]},
                {'option': 'Option 3', 'number': 3, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [4,4,4,3]},
                {'option': 'Option 4', 'number': 4, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [2,1,5,7]},
            ]
        }]

        expected_result = [{
            'type': 'BORDA',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [7,2,4,2], 'postproc': 44},
                {'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [2,8,2,3], 'postproc': 39},
                {'option': 'Option 3', 'number': 3, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [4,4,4,3], 'postproc': 39},
                {'option': 'Option 4', 'number': 4, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [2,1,5,7], 'postproc': 28},
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_borda_without_votes(self):
        data = [{
            'type': 'BORDA',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [0,0,0,0]},
                {'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [0,0,0,0]},
                {'option': 'Option 3', 'number': 3, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [0,0,0,0]},
                {'option': 'Option 4', 'number': 4, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [0,0,0,0]},
            ]
        }]

        expected_result = [{
            'type': 'BORDA',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [0,0,0,0], 'postproc': 0},
                {'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [0,0,0,0], 'postproc': 0},
                {'option': 'Option 3', 'number': 3, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [0,0,0,0], 'postproc': 0},
                {'option': 'Option 4', 'number': 4, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': [0,0,0,0], 'postproc': 0},
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_borda_without_option_attribute(self):
        with self.assertRaises(KeyError):
            data = [{
                'type': 'BORDA'
            }]

            response = self.client.post('/postproc/', data, format='json')

    def test_borda_without_options(self):
        with self.assertRaises(Exception):
            data = [{
                'type': 'BORDA',
                'options': []
            }]

            response = self.client.post('/postproc/', data, format='json')
    
    def test_equality_women_greater(self):
        data = [{
            'type': 'EQUALITY',
            'options': [
                { 'option': 'Option 1', 'number': 1, 'votes_masc': 2, 'votes_fem': 3, 'points': 0, 'votes': 0},
                { 'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 4, 'points': 0, 'votes': 0},
                { 'option': 'Option 3', 'number': 3, 'votes_masc': 3, 'votes_fem': 1, 'points': 0, 'votes': 0},
                { 'option': 'Option 4', 'number': 4, 'votes_masc': 1, 'votes_fem': 0, 'points': 0, 'votes': 0},
                { 'option': 'Option 5', 'number': 5, 'votes_masc': 1, 'votes_fem': 3, 'points': 0, 'votes': 0},
                { 'option': 'Option 6', 'number': 6, 'votes_masc': 1, 'votes_fem': 1, 'points': 0, 'votes': 0},
            ]
        }]

        expected_result = [{
            'type': 'EQUALITY',
            'options': [
                { 'option': 'Option 1', 'number': 1, 'votes_masc': 2, 'votes_fem': 3, 'points': 0, 'votes': 0, 'postproc': 4 },
                { 'option': 'Option 3', 'number': 3, 'votes_masc': 3, 'votes_fem': 1, 'points': 0, 'votes': 0, 'postproc': 4 },
                { 'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 4, 'points': 0, 'votes': 0, 'postproc': 3 },
                { 'option': 'Option 5', 'number': 5, 'votes_masc': 1, 'votes_fem': 3, 'points': 0, 'votes': 0, 'postproc': 3 },
                { 'option': 'Option 6', 'number': 6, 'votes_masc': 1, 'votes_fem': 1, 'points': 0, 'votes': 0, 'postproc': 2 },
                { 'option': 'Option 4', 'number': 4, 'votes_masc': 1, 'votes_fem': 0, 'points': 0, 'votes': 0, 'postproc': 1 },
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_equality_men_greater(self):
        data = [{
            'type': 'EQUALITY',
            'options': [
                { 'option': 'Option 1', 'number': 1, 'votes_masc': 3, 'votes_fem': 1, 'points': 0, 'votes': 0 },
                { 'option': 'Option 2', 'number': 2, 'votes_masc': 1, 'votes_fem': 2, 'points': 0, 'votes': 0 },
                { 'option': 'Option 3', 'number': 3, 'votes_masc': 2, 'votes_fem': 1, 'points': 0, 'votes': 0 },
                { 'option': 'Option 4', 'number': 4, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0 },
                { 'option': 'Option 5', 'number': 5, 'votes_masc': 1, 'votes_fem': 1, 'points': 0, 'votes': 0 },
                { 'option': 'Option 6', 'number': 6, 'votes_masc': 3, 'votes_fem': 3, 'points': 0, 'votes': 0 },
            ]
        }]

        expected_result = [{
            'type': 'EQUALITY',
            'options': [
                { 'option': 'Option 6', 'number': 6, 'votes_masc': 3, 'votes_fem': 3, 'points': 0, 'votes': 0, 'postproc': 5 },
                { 'option': 'Option 1', 'number': 1, 'votes_masc': 3, 'votes_fem': 1, 'points': 0, 'votes': 0, 'postproc': 3 },
                { 'option': 'Option 2', 'number': 2, 'votes_masc': 1, 'votes_fem': 2, 'points': 0, 'votes': 0, 'postproc': 3 },
                { 'option': 'Option 3', 'number': 3, 'votes_masc': 2, 'votes_fem': 1, 'points': 0, 'votes': 0, 'postproc': 3 },
                { 'option': 'Option 5', 'number': 5, 'votes_masc': 1, 'votes_fem': 1, 'points': 0, 'votes': 0, 'postproc': 2 },
                { 'option': 'Option 4', 'number': 4, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0, 'postproc': 0 },
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_equality_without_votes(self):
        data = [{
            'type': 'EQUALITY',
            'options': [
                { 'option': 'Option 1', 'number': 1, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0},
                { 'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0},
                { 'option': 'Option 3', 'number': 3, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0},
                { 'option': 'Option 4', 'number': 4, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0},
                { 'option': 'Option 5', 'number': 5, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0},
                { 'option': 'Option 6', 'number': 6, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0},
            ]
        }]

        expected_result = [{
            'type': 'EQUALITY',
            'options': [
                { 'option': 'Option 1', 'number': 1, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0, 'postproc': 0 },
                { 'option': 'Option 2', 'number': 2, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0, 'postproc': 0 },
                { 'option': 'Option 3', 'number': 3, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0, 'postproc': 0 },
                { 'option': 'Option 4', 'number': 4, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0, 'postproc': 0 },
                { 'option': 'Option 5', 'number': 5, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0, 'postproc': 0 },
                { 'option': 'Option 6', 'number': 6, 'votes_masc': 0, 'votes_fem': 0, 'points': 0, 'votes': 0, 'postproc': 0 },
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
    
    def test_equality_without_option_attribute(self):
        with self.assertRaises(KeyError):
            data = [{
                'type': 'EQUALITY'
            }]

            response = self.client.post('/postproc/', data, format='json')

    def test_equality_without_options(self):
        with self.assertRaises(Exception):
            data = [{
                'type': 'EQUALITY',
                'options': []
            }]

            response = self.client.post('/postproc/', data, format='json')

    def test_sainte_lague(self):
        data = [{
            'type': 'SAINTE_LAGUE',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 340000},
                {'option': 'Option 2', 'number': 2, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 280000},
                {'option': 'Option 3', 'number': 3, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 160000},
                {'option': 'Option 4', 'number': 4, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 60000},
                {'option': 'Option 5', 'number': 5, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 40000},
                {'option': 'Option 6', 'number': 6, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 20000},
                {'option': 'Option 7', 'number': 7, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 10000}
            ]
        }]

        expected_result = [{
            'type': 'SAINTE_LAGUE',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 340000, 'postproc': 3},
                {'option': 'Option 2', 'number': 2, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 280000, 'postproc': 2},
                {'option': 'Option 3', 'number': 3, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 160000, 'postproc': 1},
                {'option': 'Option 4', 'number': 4, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 60000, 'postproc': 1},
                {'option': 'Option 5', 'number': 5, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 40000, 'postproc': 0},
                {'option': 'Option 6', 'number': 6, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 20000, 'postproc': 0},
                {'option': 'Option 7', 'number': 7, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 10000, 'postproc': 0}
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_sainte_lague_without_points(self):
        data = [{
            'type': 'SAINTE_LAGUE',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 340000},
                {'option': 'Option 2', 'number': 2, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 280000},
                {'option': 'Option 3', 'number': 3, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 160000},
                {'option': 'Option 4', 'number': 4, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 60000},
                {'option': 'Option 5', 'number': 5, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 40000},
                {'option': 'Option 6', 'number': 6, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 20000},
                {'option': 'Option 7', 'number': 7, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 10000}
            ]
        }]

        expected_result = [{
            'type': 'SAINTE_LAGUE',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 340000, 'postproc': 0},
                {'option': 'Option 2', 'number': 2, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 280000, 'postproc': 0},
                {'option': 'Option 3', 'number': 3, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 160000, 'postproc': 0},
                {'option': 'Option 4', 'number': 4, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 60000, 'postproc': 0},
                {'option': 'Option 5', 'number': 5, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 40000, 'postproc': 0},
                {'option': 'Option 6', 'number': 6, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 20000, 'postproc': 0},
                {'option': 'Option 7', 'number': 7, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 10000, 'postproc': 0}
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_sainte_lague_without_votes(self):
        data = [{
            'type': 'SAINTE_LAGUE',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
                {'option': 'Option 2', 'number': 2, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
                {'option': 'Option 3', 'number': 3, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
                {'option': 'Option 4', 'number': 4, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
                {'option': 'Option 5', 'number': 5, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
                {'option': 'Option 6', 'number': 6, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
                {'option': 'Option 7', 'number': 7, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0}
            ]
        }]

        expected_result = [{
            'type': 'SAINTE_LAGUE',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 0},
                {'option': 'Option 2', 'number': 2, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 0},
                {'option': 'Option 3', 'number': 3, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 0},
                {'option': 'Option 4', 'number': 4, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 0},
                {'option': 'Option 5', 'number': 5, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 0},
                {'option': 'Option 6', 'number': 6, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 0},
                {'option': 'Option 7', 'number': 7, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 0}
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_sainte_lague_without_option_attribute(self):
        with self.assertRaises(KeyError):
            data = [{
                'type': 'SAINTE_LAGUE'
            }]

            response = self.client.post('/postproc/', data, format='json')

    def test_sainte_lague_without_options(self):
        with self.assertRaises(IndexError):
            data = [{
                'type': 'SAINTE_LAGUE',
                'options': []
            }]

            response = self.client.post('/postproc/', data, format='json')

    def test_hondt(self):
        data = [{
            'type': 'HONDT',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 340000},
                {'option': 'Option 2', 'number': 2, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 280000},
                {'option': 'Option 3', 'number': 3, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 160000},
                {'option': 'Option 4', 'number': 4, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 60000},
                {'option': 'Option 5', 'number': 5, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 15000},
            ]
        }]

        expected_result = [{
            'type': 'HONDT',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 340000, 'postproc': 3},
                {'option': 'Option 2', 'number': 2, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 280000, 'postproc': 3},
                {'option': 'Option 3', 'number': 3, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 160000, 'postproc': 1},
                {'option': 'Option 4', 'number': 4, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 60000, 'postproc': 0},
                {'option': 'Option 5', 'number': 5, 'points': 7, 'votes_masc': 0, 'votes_fem': 0, 'votes': 15000, 'postproc': 0},
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
        
    def test_droop(self):
        data = [{
            'type': 'DROOP',
            'options': [
                { 'option': 'Option A', 'number': 1, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 12000 },
                { 'option': 'Option B', 'number': 2, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 184000 },
                { 'option': 'Option C', 'number': 3, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 73000 },
                { 'option': 'Option D', 'number': 4, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 2000 },
                { 'option': 'Option E', 'number': 5, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 391000 },
                { 'option': 'Option F', 'number': 6, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 311000 },
                { 'option': 'Option G', 'number': 7, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 27000 },
            ]
        }]

        expected_result = [{
            'type': 'DROOP',
            'options': [
                { 'option': 'Option E', 'number': 5, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 391000, 'postproc': 8 },
                { 'option': 'Option F', 'number': 6, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 311000, 'postproc': 7 },
                { 'option': 'Option B', 'number': 2, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 184000, 'postproc': 4 },
                { 'option': 'Option C', 'number': 3, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 73000, 'postproc': 2 },
                { 'option': 'Option G', 'number': 7, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 27000, 'postproc': 0},
                { 'option': 'Option A', 'number': 1, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 12000, 'postproc': 0 },
                { 'option': 'Option D', 'number': 4, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 2000, 'postproc': 0 },
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_droop_without_points(self):
        data = [{
            'type': 'DROOP',
            'options': [
                { 'option': 'Option A', 'number': 1, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 12000 },
                { 'option': 'Option B', 'number': 2, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 184000 },
                { 'option': 'Option C', 'number': 3, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 73000 },
                { 'option': 'Option D', 'number': 4, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 2000 },
                { 'option': 'Option E', 'number': 5, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 391000 },
                { 'option': 'Option F', 'number': 6, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 311000 },
                { 'option': 'Option G', 'number': 7, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 27000 },
            ]
        }]

        expected_result = [{
            'type': 'DROOP',
            'options': [
                { 'option': 'Option E', 'number': 5, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 391000, 'postproc': 0  },
                { 'option': 'Option F', 'number': 6, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 311000, 'postproc': 0 },
                { 'option': 'Option B', 'number': 2, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 184000, 'postproc': 0 },
                { 'option': 'Option C', 'number': 3, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 73000, 'postproc': 0 },
                { 'option': 'Option G', 'number': 7, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 27000, 'postproc': 0 },
                { 'option': 'Option A', 'number': 1, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 12000, 'postproc': 0 },
                { 'option': 'Option D', 'number': 4, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 2000, 'postproc': 0 },
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_droop_without_votes(self):
        data = [{
            'type': 'DROOP',
            'options': [
                { 'option': 'Option A', 'number': 1, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0 },
                { 'option': 'Option B', 'number': 2, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0 },
                { 'option': 'Option C', 'number': 3, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0 },
                { 'option': 'Option D', 'number': 4, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0 },
                { 'option': 'Option E', 'number': 5, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0 },
                { 'option': 'Option F', 'number': 6, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0 },
                { 'option': 'Option G', 'number': 7, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0 },
            ]
        }]

        expected_result = [{
            'type': 'DROOP',
            'options': [
                { 'option': 'Option A', 'number': 1, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 15 },
                { 'option': 'Option B', 'number': 2, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 1 },
                { 'option': 'Option C', 'number': 3, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 1 },
                { 'option': 'Option D', 'number': 4, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 1 },
                { 'option': 'Option E', 'number': 5, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 1 },
                { 'option': 'Option F', 'number': 6, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 1 },
                { 'option': 'Option G', 'number': 7, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0, 'postproc': 1 },
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_droop_without_option_attribute(self):
        with self.assertRaises(KeyError):
            data = [{
                'type': 'DROOP'
            }]

            response = self.client.post('/postproc/', data, format='json')

    def test_droop_without_options(self):
        with self.assertRaises(Exception):
            data = [{
                'type': 'DROOP',
                'options': []
            }]

            response = self.client.post('/postproc/', data, format='json')

    def test_imperiali(self):
        data = [{
            'type': 'IMPERIALI',
            'options': [
                { 'option': 'Option A', 'number': 1, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 12000 },
                { 'option': 'Option B', 'number': 2, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 184000 },
                { 'option': 'Option C', 'number': 3, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 73000 },
                { 'option': 'Option D', 'number': 4, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 2000 },
                { 'option': 'Option E', 'number': 5, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 391000 },
                { 'option': 'Option F', 'number': 6, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 311000 },
                { 'option': 'Option G', 'number': 7, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 27000 },
            ]
        }]

        expected_result = [{
            'type': 'IMPERIALI',
            'options': [
                { 'option': 'Option E', 'number': 5, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 391000, 'postproc': 9 },
                { 'option': 'Option F', 'number': 6, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 311000, 'postproc': 7 },
                { 'option': 'Option B', 'number': 2, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 184000, 'postproc': 4 },
                { 'option': 'Option C', 'number': 3, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 73000, 'postproc': 1 },
                { 'option': 'Option G', 'number': 7, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 27000, 'postproc': 0},
                { 'option': 'Option A', 'number': 1, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 12000, 'postproc': 0 },
                { 'option': 'Option D', 'number': 4, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 2000, 'postproc': 0 },
            ]
        }]
   
        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

     
    def test_hare(self):
        data = [{
            'type': 'HARE',
            'options': [
                { 'option': 'Option A', 'number': 1, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 391000 },
                { 'option': 'Option B', 'number': 2, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 311000 },
                { 'option': 'Option C', 'number': 3, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 184000 },
                { 'option': 'Option D', 'number': 4, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 73000 },
                { 'option': 'Option E', 'number': 5, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 27000 },
                { 'option': 'Option F', 'number': 6, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 12000 },
                { 'option': 'Option G', 'number': 7, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 2000 },
            ]
        }]

        expected_result = [{
            'type': 'HARE',
            'options': [
                { 'option': 'Option A', 'number': 1, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 391000, 'postproc': 8 },
                { 'option': 'Option B', 'number': 2, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 311000, 'postproc': 6 },
                { 'option': 'Option C', 'number': 3, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 184000, 'postproc': 4 },
                { 'option': 'Option D', 'number': 4, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 73000, 'postproc': 2 },
                { 'option': 'Option E', 'number': 5, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 27000, 'postproc': 1},
                { 'option': 'Option F', 'number': 6, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 12000, 'postproc': 0 },
                { 'option': 'Option G', 'number': 7, 'points': 21, 'votes_masc': 0, 'votes_fem': 0, 'votes': 2000, 'postproc': 0 },
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
