#include <iostream>
#include <fstream>
#include <set>
#include <map>
#include <cmath>
#include <cstdlib> 
#include <sstream>
#include <algorithm>
#include <iterator>
#include <vector>
#include <string>

using namespace std;

bool isfloat(wstring s) {
	if (s[0] == L'-' || isdigit(s[0])) return true;
	return false;
}

double tofloat(wstring s) {
	wstringstream ss(s);
	double d;
	ss >> d;
	return d;	
}


int main(int argc, char** argv) {
	locale::global(locale(""));
	string infile_fn(argv[1]);
	string out1=infile_fn+".wfst";
	string out2=infile_fn+".wfsa";
	string in1= infile_fn;
	wifstream fin(in1.c_str());
	wofstream fout(out1.c_str());
	wofstream fout2(out2.c_str());
	wstring l = L"",s;
	int order;
	double score,backoff;
	wstring dest;
	while (l[0] != L'n') getline(fin,l);
	while (l[0] == L'n') {getline(fin,l); order++;}
	int current_ngram = 1;
	fout << "FINAL" << endl;
	fout << "(START (<s> \"<s>\" \"<s>\" 1!))" << endl;
	fout2 << "FINAL" << endl;
	fout2 << "(START (<s> *e* \"<s>\" 1!))" << endl;
	while (getline(fin,l)) {
		if (l[0] == L'\\') {current_ngram++; cout << current_ngram << endl; continue;}
		wstringstream ss(l);	
		vector<wstring> data;
		while (ss >> s) data.push_back(s);
		if (current_ngram > 0 && data.size() > 1 && isfloat(data[0])) {
			score=pow(10.0,tofloat(data[0]));
			//if (score < 0.1) continue;
			if (current_ngram == 1) {
				//cout << data[1] << " " << score << endl;
				if (data.size() > 2) {
					backoff = pow(10.0,tofloat(data[2]));
					dest = data[1];
					fout << "(" << data[1] << "  (NULL *e* *e* " << backoff << "!))" << endl;
					fout2 << "(" << data[1] << "  (NULL *e* *e* " << backoff << "!))" << endl;
				} 
				else {
					if (data[1] == L"</s>")
						dest = data[1];
					else
						dest = L"NULL";
				}				
				if (dest != L"<s>") {
					if (data[current_ngram] == L"</s>") dest = L"FINAL";
					fout  << "(NULL (" << dest << " \"" << data[1] << "\" \"" << data[1] << "\" " << score << "!))" << endl;
					fout2 << "(NULL (" << dest << " *e* \"" << data[1] << "\" " << score << "!))" << endl;
				}
				continue;
			}
			if (current_ngram < order) {
				if (data.size() > current_ngram+1) {
					backoff = pow(10.0,tofloat(data[current_ngram+1]));
					// dest = L"";
					// for (int i = 1; i <= current_ngram; i++) dest+=data[i];
					dest = data[1];
					for (int i = 2; i <= current_ngram; i++) dest += L"."+data[i];
					// wstring _dest = L"";
					// for (int i = 2; i <= current_ngram; i++) _dest+=data[i];
					wstring _dest = data[2];
					for (int i = 3; i <= current_ngram; i++) _dest+= L"."+data[i];
					fout << L"(" << dest << " (" << _dest <<  " *e* *e* " << backoff << "!))" << endl;
					fout2 << L"(" << dest << " (" << _dest <<  " *e* *e* " << backoff << "!))" << endl;
				}
				else {
					// dest = L"";
					// for (int i = 2; i <= current_ngram; i++) dest+=data[i];
					dest = data[2];
					for (int i = 3; i <= current_ngram; i++) dest+= L"."+data[i];
				}
				// wstring dest_ = L"";
				// for (int i = 1; i < current_ngram; i++) dest_+=data[i];
				wstring dest_ = data[1];
				for (int i = 2; i < current_ngram; i++) dest_+= L"."+data[i];
				if (data[current_ngram] == L"</s>") dest = L"FINAL";
				fout << "(" << dest_ <<  " (" << dest << " \"" << data[current_ngram] << "\" \"" << data[current_ngram] << "\" " << score << "!))" << endl;
				fout2 << "(" << dest_ <<  " (" << dest << " *e* \"" << data[current_ngram] << "\" " << score << "!))" << endl;
				continue;
			}
			if (current_ngram == order) {
				// wstring dest_ = L"";
				// for (int i = 1; i < current_ngram; i++) dest_+=data[i];
				wstring dest_ = data[1];
				for (int i = 2; i < current_ngram; i++) dest_+= L"."+data[i];
				// dest = L"";
				// for (int i = 2; i <= current_ngram; i++) dest+=data[i];
				dest = data[2];
				for (int i = 3; i <= current_ngram; i++) dest += L"."+data[i];
				if (data[current_ngram] == L"</s>") dest = L"FINAL";
				fout << "(" << dest_ << " (" << dest << " \"" << data[current_ngram] << "\" \"" << data[current_ngram] << "\" " << score << "!))" << endl;
				fout2 << "(" << dest_ << " (" << dest << " *e* \"" << data[current_ngram] << "\" " << score << "!))" << endl;
			}
			
		}
	}
	return 0;
}
